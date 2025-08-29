# flights/createFlightDesignator.py
import grpc
import datetime
from typing import Tuple, Optional
from google.protobuf import duration_pb2, timestamp_pb2
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc, flight_designator_pb2
import constants


def _tz() -> str:
    return getattr(constants, "ORIGIN_AIRPORT_TZ", None) or getattr(constants, "FLIGHT_TIMEZONE", "UTC")


def _clock_to_time(hhmm: str) -> datetime.time:
    h, m = [int(x) for x in hhmm.split(":")]
    return datetime.time(hour=h, minute=m, second=0)


def _compute_times_from_constants() -> tuple[datetime.time, datetime.time, datetime.time, datetime.time]:
    """Return (boarding, departure, arrival, gate_close) with strict ordering."""
    mode = (getattr(constants, "FLIGHT_TIMES_MODE",
            "OFFSETS") or "OFFSETS").upper()
    if mode == "CLOCK":
        boarding = _clock_to_time(constants.FLIGHT_BOARDING_CLOCK)
        depart = _clock_to_time(constants.FLIGHT_DEPARTURE_CLOCK)
        arrive = _clock_to_time(constants.FLIGHT_ARRIVAL_CLOCK)
        gate = _clock_to_time(constants.FLIGHT_GATECLOSE_CLOCK)
    else:
        dep_dt = datetime.datetime.fromisoformat(
            constants.FLIGHT_DEPARTURE_ISO)
        if dep_dt.tzinfo is None:
            dep_dt = dep_dt.replace(tzinfo=datetime.timezone.utc)
        boarding_dt = dep_dt - \
            datetime.timedelta(minutes=constants.BOARDING_MIN_BEFORE_DEP)
        arrive_dt = dep_dt + \
            datetime.timedelta(minutes=constants.ARRIVAL_MIN_AFTER_DEP)
        gate_dt = dep_dt - \
            datetime.timedelta(minutes=constants.GATE_CLOSE_MIN_BEFORE_DEP)
        boarding, depart, arrive, gate = (
            boarding_dt.timetz().replace(tzinfo=None),
            dep_dt.timetz().replace(tzinfo=None),
            arrive_dt.timetz().replace(tzinfo=None),
            gate_dt.timetz().replace(tzinfo=None),
        )

    def to_secs(t: datetime.time) -> int:
        return t.hour*3600 + t.minute*60 + t.second

    b, g, d, a = to_secs(boarding), to_secs(
        gate), to_secs(depart), to_secs(arrive)
    if g <= b:
        g = b + 60
    if d <= g:
        d = g + 60
    if a <= d:
        a = d + 60

    def from_secs(s: int) -> datetime.time:
        h = s // 3600
        s %= 3600
        m = s // 60
        s %= 60
        return datetime.time(h, m, s)

    return from_secs(b), from_secs(d), from_secs(a), from_secs(g)


def _to_duration(t: datetime.time) -> duration_pb2.Duration:
    return duration_pb2.Duration(seconds=t.hour*3600 + t.minute*60 + t.second)


def _to_timestamp_today(t: datetime.time) -> timestamp_pb2.Timestamp:
    now = datetime.datetime.now(datetime.timezone.utc)
    dt = now.replace(hour=t.hour, minute=t.minute,
                     second=t.second, microsecond=0)
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(dt)
    return ts


def _assign_time_like(container, field_name: str, t: datetime.time) -> bool:
    if not hasattr(container, field_name):
        return False
    f = container.DESCRIPTOR.fields_by_name.get(field_name)
    if f is None:
        return False
    # Duration
    if f.message_type and f.message_type.full_name.endswith("google.protobuf.Duration"):
        getattr(container, field_name).CopyFrom(_to_duration(t))
        return True
    # Timestamp
    if f.message_type and f.message_type.full_name.endswith("google.protobuf.Timestamp"):
        getattr(container, field_name).CopyFrom(_to_timestamp_today(t))
        return True
    # google.type.TimeOfDay
    if f.message_type and f.message_type.full_name.endswith("google.type.TimeOfDay"):
        tod = getattr(container, field_name)
        if hasattr(tod, "hours"):
            tod.hours = t.hour
        if hasattr(tod, "minutes"):
            tod.minutes = t.minute
        if hasattr(tod, "seconds"):
            tod.seconds = t.second
        return True
    # string "HH:MM:SS"
    if f.type == f.TYPE_STRING:
        setattr(container, field_name,
                f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}")
        return True
    # numeric seconds
    if f.type in (f.TYPE_INT32, f.TYPE_INT64, f.TYPE_UINT32, f.TYPE_UINT64):
        setattr(container, field_name, t.hour*3600 + t.minute*60 + t.second)
        return True
    return False


def _set_date_y_m_d(msg, dt: datetime.date) -> bool:
    wrote = False
    if hasattr(msg, "year"):
        msg.year = dt.year
        wrote = True
    if hasattr(msg, "month"):
        msg.month = dt.month
        wrote = True
    if hasattr(msg, "day"):
        msg.day = dt.day
        wrote = True
    return wrote


def _build_schedule(fd_msg) -> None:
    """
    Attach a valid Schedule with a populated nested flightSchedule submessage.
    Your server’s validator requires Schedule.flightSchedule, so we error if it’s missing.
    """
    # Locate Schedule field on FlightDesignator
    sched_field_name = "Schedule" if hasattr(fd_msg, "Schedule") else (
        "schedule" if hasattr(fd_msg, "schedule") else None)
    if not sched_field_name:
        raise RuntimeError(
            "FlightDesignator has no Schedule/schedule field, but server requires it.")
    sched_field = fd_msg.DESCRIPTOR.fields_by_name.get(sched_field_name)
    if not sched_field or not sched_field.message_type:
        raise RuntimeError("Schedule field is not a message; cannot populate.")

    # Construct Schedule message (concrete type)
    ScheduleMsg = getattr(flight_designator_pb2, sched_field.message_type.name, None) \
        or sched_field.message_type._concrete_class  # type: ignore[attr-defined]
    schedule = ScheduleMsg()

    # Must have nested flightSchedule
    fs_field_name = None
    for name in ("flightSchedule", "FlightSchedule"):
        if hasattr(schedule, name):
            fs_field_name = name
            break
    if not fs_field_name:
        raise RuntimeError(
            "Schedule.flightSchedule is required by server but missing in this build.")

    # Build nested flightSchedule message
    fs_desc = schedule.DESCRIPTOR.fields_by_name.get(fs_field_name)
    if not fs_desc or not fs_desc.message_type:
        raise RuntimeError(
            "Schedule.flightSchedule field is not a message; cannot populate.")
    FSMsg = getattr(flight_designator_pb2, fs_desc.message_type.name, None) \
        or fs_desc.message_type._concrete_class  # type: ignore[attr-defined]
    fs = FSMsg()

    # Times from constants
    boarding_t, depart_t, arrive_t, gate_t = _compute_times_from_constants()

    def fill_times(container) -> None:
        wrote = False
        wrote |= _assign_time_like(container, "boardingTime", boarding_t)
        wrote |= _assign_time_like(container, "gateClosingTime", gate_t)
        wrote |= _assign_time_like(
            container, "scheduledDepartureTime", depart_t)
        wrote |= _assign_time_like(container, "scheduledArrivalTime", arrive_t)
        wrote |= _assign_time_like(container, "departureTime", depart_t)
        wrote |= _assign_time_like(container, "arrivalTime", arrive_t)
        if not wrote:
            for fname, tt in (("start", depart_t), ("end", arrive_t)):
                _assign_time_like(container, fname, tt)

    # Place times inside fs
    placed = False
    for name in ("times", "weekTimes", "defaultTimes", "flightTimes", "time"):
        if hasattr(fs, name):
            fill_times(getattr(fs, name))
            placed = True
            break
    if not placed:
        days = ("monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday")
        if any(hasattr(fs, d) for d in days):
            for d in days:
                if hasattr(fs, d):
                    fill_times(getattr(fs, d))
            placed = True
    if not placed:
        fill_times(fs)  # last resort: directly on fs

    # Timezone on fs if present
    for tz_field in ("ianaTimezone", "timezone", "timeZone", "tz"):
        if hasattr(fs, tz_field):
            setattr(fs, tz_field, _tz())
            break

    # Weekday enable flags if present (harmless if absent)
    for flag in ("operatesMonday", "operatesTuesday", "operatesWednesday", "operatesThursday",
                 "operatesFriday", "operatesSaturday", "operatesSunday"):
        if hasattr(fs, flag):
            setattr(fs, flag, True)

    # Optional effective date range (harmless if absent)
    today = datetime.date.today()
    start = today
    end = today + datetime.timedelta(days=365)
    for start_field in ("startDate", "effectiveFrom"):
        if hasattr(fs, start_field):
            _set_date_y_m_d(getattr(fs, start_field), start)
            break
    for end_field in ("endDate", "effectiveTo"):
        if hasattr(fs, end_field):
            _set_date_y_m_d(getattr(fs, end_field), end)
            break

    # Attach nested flightSchedule to schedule, and schedule to designator
    getattr(schedule, fs_field_name).CopyFrom(fs)
    getattr(fd_msg, sched_field_name).CopyFrom(schedule)


def run(
    channel: grpc.Channel,
    *,
    carrier_code: str,
    flight_number: str,
    pass_template_id: str,
    origin: str,
    destination: str,
    revision: Optional[int] = None,
) -> Tuple[Optional[str], bool]:
    stub = flights_grpc.FlightsStub(channel)

    # revision from constants (must be > 0)
    if revision is None:
        revision = getattr(constants, "FLIGHT_DESIGNATOR_REVISION", 1) or 1
    if revision <= 0:
        revision = 1

    # Skip if already exists (best-effort)
    Req = getattr(flight_designator_pb2, "FlightDesignatorRequest", None)
    getter = getattr(stub, "getFlightDesignator", None) or getattr(
        stub, "GetFlightDesignator", None)
    if Req is not None and getter is not None:
        try:
            req = Req()
            if hasattr(req, "carrierCode"):
                req.carrierCode = carrier_code
            if hasattr(req, "flightNumber"):
                req.flightNumber = flight_number
            if hasattr(req, "revision"):
                req.revision = revision
            if hasattr(req, "flightDesignator"):
                fd0 = req.flightDesignator
                if hasattr(fd0, "carrierCode"):
                    fd0.carrierCode = carrier_code
                if hasattr(fd0, "flightNumber"):
                    fd0.flightNumber = flight_number
                if hasattr(fd0, "revision"):
                    fd0.revision = revision
            _ = getter(req)
            print(
                f"Flight designator {carrier_code}{flight_number} rev={revision} already exists")
            return None, True
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.NOT_FOUND:
                raise

    # Build designator
    fd = flight_designator_pb2.FlightDesignator()
    if hasattr(fd, "carrierCode"):
        fd.carrierCode = carrier_code
    if hasattr(fd, "flightNumber"):
        fd.flightNumber = flight_number
    if hasattr(fd, "revision"):
        fd.revision = revision
    if hasattr(fd, "passTemplateId"):
        fd.passTemplateId = pass_template_id
    if hasattr(fd, "origin"):
        fd.origin = origin
    if hasattr(fd, "destination"):
        fd.destination = destination

    # Put timezone on designator if supported
    for tz_field in ("ianaTimezone", "timezone", "timeZone", "tz"):
        if hasattr(fd, tz_field):
            setattr(fd, tz_field, _tz())
            break

    # REQUIRED schedule
    _build_schedule(fd)

    # Create, handle already-exists
    try:
        resp = stub.createFlightDesignator(fd)
        designator_id = getattr(resp, "id", "") or getattr(
            resp, "flightDesignatorId", "")
        print(
            f"Created flight designator: {designator_id or ''} ({carrier_code}{flight_number}) rev={revision}")
        return designator_id or None, False
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            print(
                f"Flight designator already exists: {carrier_code}{flight_number} rev={revision}")
            return None, True
        raise
