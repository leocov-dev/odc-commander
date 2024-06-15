from odc_commander.commands.basic_params import FloatArrayParam, FloatParam

# -----------------------------------------------------------------------------
# DYNAMIC CLAMP RUNTIME PARAMETERS

# Parameters are processed by list order.
# The same list order must be maintained here
# and in the `dynamic_clamp.ino` firmware for
# correct assignment.
RUNTIME_PARAMS = FloatArrayParam(
    "FunctionParameters",
    FloatParam(0.0, "Shunt"),
    FloatParam(1.0, "HCN"),
    FloatParam(2.0, "Na"),
    FloatParam(3.0, "OU_exc_mean"),
    FloatParam(4.0, "OU_exc_D"),
    FloatParam(5.0, "OU_inh_mean"),
    FloatParam(6.0, "OU_inh_D"),
    FloatParam(7.0, "EPSC"),
)
