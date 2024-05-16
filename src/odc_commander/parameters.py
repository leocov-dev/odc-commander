from odc_commander.commands.basic_params import FloatParam

# -----------------------------------------------------------------------------
# DYNAMIC CLAMP RUNTIME PARAMETERS
#
# Parameters are processed by list order.
# The same list order must be maintained here
# and in the `dynamic_clamp.ino` firmware for
# correct assignment.
RUNTIME_PARAMS = [
    FloatParam(0.0, "Shunt"),
    FloatParam(0.0, "HCN"),
    FloatParam(0.0, "Na"),
    FloatParam(0.0, "OU_exc_mean"),
    FloatParam(0.0, "OU_exc_D"),
    FloatParam(0.0, "OU_inh_mean"),
    FloatParam(0.0, "OU_inh_D"),
    FloatParam(0.0, "EPSC"),
]
