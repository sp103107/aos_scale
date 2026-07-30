from best_buds_weight_station.envelope import validate_envelope, ack_for, terminal_for


def handle_envelope(envelope, handler):
    env = validate_envelope(envelope)
    ack = ack_for(env)
    try:
        result = handler(env["payload"])
        terminal = terminal_for(env, "success", result)
    except Exception as exc:
        terminal = terminal_for(env, "failure", error={"error_code": type(exc).__name__, "operator_message": "The command failed. Review the application receipt and recovery guidance."})
    return ack, terminal
