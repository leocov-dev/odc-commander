from odc_commander.commands.basic_params import FloatArrayParam, FloatParam

# -----------------------------------------------------------------------------
# DYNAMIC CLAMP RUNTIME PARAMETERS

# Parameters are processed by list order.
# The same list order must be maintained here
# and in the `dynamic_clamp.ino` firmware for
# correct assignment.
RUNTIME_PARAMS = FloatArrayParam(
    "FunctionParameters",
    FloatParam(value=0.0, label="Shunt"),
    FloatParam(value=1.0, label="HCN"),
    FloatParam(value=2.0, label="Na"),
    FloatParam(value=3.0, label="OU_exc_mean"),
    FloatParam(value=4.0, label="OU_exc_D"),
    FloatParam(value=5.0, label="OU_inh_mean"),
    FloatParam(value=6.0, label="OU_inh_D"),
    FloatParam(value=7.0, label="EPSC"),
)
