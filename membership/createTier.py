# membership/createTier.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc as member_grpc, tier_pb2
from passkit.io.core import a_rpc_templates_pb2_grpc as templates_grpc
from passkit.io.common import template_pb2


def run(channel: grpc.Channel, program_id: str) -> str:
    """
    Creates a default template and a base Tier under the given program_id.
    Returns the created tier id.
    """
    if not program_id:
        raise ValueError("program_id is required to create a Tier")

    # Stubs
    members = member_grpc.MembersStub(channel)
    templates = templates_grpc.TemplatesStub(channel)

    # --- Create a default template ---
    req = template_pb2.DefaultTemplateRequest()
    # Some schemas expect a string "MEMBERSHIP"; others an enum. The string works for many setups.
    req.protocol = "MEMBERSHIP"
    req.revision = 1

    try:
        template = templates.GetDefaultTemplate(req)
    except AttributeError:
        template = templates.getDefaultTemplate(req)

    # Customize template
    template.name = "Quickstart Base Tier"
    template.description = "Quickstart Base Tier Pass"
    template.timezone = "Europe/London"

    try:
        created_tpl = templates.CreateTemplate(template)
    except AttributeError:
        created_tpl = templates.createTemplate(template)

    pass_template_id = getattr(created_tpl, "id", "")
    print("Created template:", pass_template_id)

    # --- Create Tier ---
    tier = tier_pb2.Tier()
    tier.id = "base"
    tier.tierIndex = 1
    tier.name = "Quickstart Base Tier"
    tier.passTemplateId = pass_template_id
    tier.programId = program_id
    tier.timezone = "Europe/London"

    created_tier = members.createTier(tier)

    tier_id = getattr(created_tier, "id", "")
    print("Created tier:", tier_id)
    return tier_id


# Optional: allow standalone run for testing
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    from membership.createProgram import run as create_program
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        pid = create_program(ch)
        run(ch, pid)
    finally:
        pool.close()
