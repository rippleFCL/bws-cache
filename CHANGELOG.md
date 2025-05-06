# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [server-v2.6.0] - 2025-05-06
### :sparkles: New Features
- [`65d8074`](https://github.com/rippleFCL/bws-cache/commit/65d8074b2f79a56f94382378595959ca94956890) - add region settings and allow requests to overwrite bwsc defaults
- [`359aa63`](https://github.com/rippleFCL/bws-cache/commit/359aa633257c5d0d20fba11187e339467a2a13c6) - **secret.py**: added headers to ansible lookup plugin

### :bug: Bug Fixes
- [`5a3d38a`](https://github.com/rippleFCL/bws-cache/commit/5a3d38a9b3a345315c01cdc4b1e30e35b603d830) - **deps**: update dependency fastapi to v0.115.12 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`f58f866`](https://github.com/rippleFCL/bws-cache/commit/f58f8662068a522fb2592dde5518c1e54ce1cd7d) - **deps**: update dependency uvicorn to v0.34.2 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`241d259`](https://github.com/rippleFCL/bws-cache/commit/241d259522082a29c8ccbfc25350c25254e0f68d) - **client.py**: fix xor to be better
- [`40c54c9`](https://github.com/rippleFCL/bws-cache/commit/40c54c9f0a1c2bbf2a07fa3a65c6d91f365ed583) - **build.yml**: fix incorect tagging
- [`8a39e76`](https://github.com/rippleFCL/bws-cache/commit/8a39e76540131c82376468668246b495d197a404) - **build.yml**: remove redundant image git tag

### :wrench: Chores
- [`bdfe14e`](https://github.com/rippleFCL/bws-cache/commit/bdfe14ede81dda7db5ba4eb211498b7f933bc44f) - **deps**: update dependency ansible-core to v2.18.5 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`1164bc5`](https://github.com/rippleFCL/bws-cache/commit/1164bc596614925bdd463f4183432946965eb4fd) - **deps**: update dependency ruff to v0.11.7 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`16561f2`](https://github.com/rippleFCL/bws-cache/commit/16561f2c08e25a6df5037440b1ceeccaa8634799) - **deps**: update ansible/ansible-lint action to v25.4.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`2588031`](https://github.com/rippleFCL/bws-cache/commit/25880313e2eb5fc9d7770d8661fd93d7e42c7bb0) - **deps**: update dependency ruff to v0.11.8 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`8cc7289`](https://github.com/rippleFCL/bws-cache/commit/8cc7289060b4f63dc8bd1152364d4701f473bc34) - **poetry**: add pre-commit dep and poetry venv location settings
- [`cffabde`](https://github.com/rippleFCL/bws-cache/commit/cffabde7ffd22577a480884f7c64e7edebb9384a) - move precommit to dev dep group
- [`5660453`](https://github.com/rippleFCL/bws-cache/commit/5660453fe87c816e4f2e7dd9f7f237fe222d312a) - **README.md**: change readme to reflect new features
- [`f29398b`](https://github.com/rippleFCL/bws-cache/commit/f29398bd51a7cc1dd73ff5c350f917ad42ce566c) - **README**: improved via the tig tooling
- [`dded2ed`](https://github.com/rippleFCL/bws-cache/commit/dded2ed88b0e7a7cf1404a66d35e4412e8c3304b) - **README**: change header type


## [server-v2.5.0] - 2025-03-20
### :sparkles: New Features
- [`830dfc3`](https://github.com/rippleFCL/bws-cache/commit/830dfc380ca97e703f3d520e16e53015bbe8b47d) - **prom_client**: add the stats endpoint data to the metrics endpoint *(commit by [@rippleFCL](https://github.com/rippleFCL))*

### :bug: Bug Fixes
- [`7261b6f`](https://github.com/rippleFCL/bws-cache/commit/7261b6f035c4804a51c3bf85868d98fe1de0aa38) - **deps**: update dependency fastapi to v0.115.11 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`739cd14`](https://github.com/rippleFCL/bws-cache/commit/739cd14c21861a7233b057b2f7ecdc582e4f35f8) - **prom_export**: remove unused import *(commit by [@rippleFCL](https://github.com/rippleFCL))*

### :wrench: Chores
- [`1210c4d`](https://github.com/rippleFCL/bws-cache/commit/1210c4d8f0e6280646280cb3fa8ef8d8f7e22088) - **deps**: update ansible/ansible-lint action to v25.1.3 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`37914dd`](https://github.com/rippleFCL/bws-cache/commit/37914dd946ddd59bc62ab5a3342cc1de2a22aa1b) - **deps**: update dependency ansible-core to v2.18.3 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`700ef8f`](https://github.com/rippleFCL/bws-cache/commit/700ef8f355e587fd6e4bc03a4271f741a0636ff3) - **deps**: update dependency ruff to ^0.11.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*


## [v2.4.2] - 2025-02-05
### :bug: Bug Fixes
- [`1beff3c`](https://github.com/rippleFCL/bws-cache/commit/1beff3c4b1632224cade8bdba3c99805a45196a7) - **client**: fix not sleeping between multiple client refreshes *(commit by [@rippleFCL](https://github.com/rippleFCL))*

### :recycle: Refactors
- [`eb6e70c`](https://github.com/rippleFCL/bws-cache/commit/eb6e70c88fc72d49738b4c1e951364e5ca1edc97) - **client**: fix incorrect spellings *(commit by [@rippleFCL](https://github.com/rippleFCL))*
- [`6aed836`](https://github.com/rippleFCL/bws-cache/commit/6aed836093c65e5466f94a6017662754a9bb3b8a) - **client**: fix spelling mistakes *(commit by [@rippleFCL](https://github.com/rippleFCL))*

[v2.4.2]: https://github.com/rippleFCL/bws-cache/compare/v2.4.1...v2.4.2
[server-v2.5.0]: https://github.com/rippleFCL/bws-cache/compare/ansible-v1.1.0...server-v2.5.0
[server-v2.6.0]: https://github.com/rippleFCL/bws-cache/compare/ansible-v1.1.1...server-v2.6.0
