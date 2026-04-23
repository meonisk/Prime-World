# server/

All backend services. Four independent stacks live side by side:

| Sub-tree | Purpose | Language | Process model |
|----------|---------|----------|---------------|
| `battle/` | PvX battle simulation cluster (the in-match server) | C++ | Many roles launched by `UniServerApp-*.cmd` |
| `social/` | Profiles, friends, parties, guilds, chat, sieges, billing, matchmaking | Python (Tornado) | `pwserver.py`, `bro.py`, `coordinator.py` + dozens of `*_service.py` daemons |
| `socagr/` | Aggregator, billing, GM tooling, web admin | PHP (Zend-style MVC) | `application/background/startWorkers.php`, `application/frontend` |
| `control-center/` | Cluster management UI | C# (.NET) | `ClusterManagement/` |

## battle/

`battle/src/Server/` — the C++ source tree (Coordinator, MatchMaking, Relay,
Chat, NewLogin, Monitoring, RPC, NetworkAIO, ClusterAdmin, …).

`battle/build/` — pre-built deliverable. `Bin/` contains 20+ `*.cmd` scripts,
each launching a different role of the cluster (coordinator, lobby, gateway,
gamesvc, gamebalancer, chat, livemm, relay, monitoring, clusteradmin,
clientctrl, login, …).

`battle/build/Data/` is a 25 k-file mirror of `assets/`. See
[REPO_STRUCTURE.md §6.3](../docs/REPO_STRUCTURE.md#6-known-follow-ups) — open
work to dedupe.

## social/

Tornado-based Python backend. Largest single files:
- `pwserver.py` — main server entry
- `friend_service.py`, `chat_service.py`, `siege_service.py`, `party_service.py` — per-domain services
- `coordinator.py` — service coordination
- `bro.py` — broker / message dispatch

Subfolders: `base/`, `batch/`, `bin/`, `cfg/`, `config/`, `enums/`, `ext_main/`,
`ext_pw/`, `friendsdata/`, `guild/`, `libs/`, `linux/`, `logic/`, `mail/`,
`mdutils/`, `modeldata/`, `party/`, `services/`, `siege/`, `testdata/`,
`tests/`, `thrift_pw/`, `tools/`, `tornado/`, `vendor/`, `xdb/`.

## socagr/

PHP backend, classic Zend MVC layout: `application/`, `library/`, `misc/`,
`www/`. Web frontend + background workers.

## control-center/

`.NET` cluster management — `ClusterManagement/`.

## See also

- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) §2.2
- [Windows_trunk_cluster_client_configuration - Prog - Nival Network.pdf](../docs/Windows_trunk_cluster_client_configuration%20-%20Prog%20-%20Nival%20Network.pdf) — original ops doc
- [Тестирование Social - Prog - Nival Network.pdf](../docs/Тестирование%20Social%20-%20Prog%20-%20Nival%20Network.pdf) — social-server testing guide
