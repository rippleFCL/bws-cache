# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [server-v3.0.0] - 2025-07-15
### :boom: BREAKING CHANGES
- due to [`a181559`](https://github.com/rippleFCL/bws-cache/commit/a181559fc79ca66937d3a9bde3fd317def9d2e09) - switched to bws-sdk *(commit by [@rippleFCL](https://github.com/rippleFCL))*:

  switched to bws-sdk


### :sparkles: New Features
- [`a181559`](https://github.com/rippleFCL/bws-cache/commit/a181559fc79ca66937d3a9bde3fd317def9d2e09) - switched to bws-sdk *(commit by [@rippleFCL](https://github.com/rippleFCL))*

### :bug: Bug Fixes
- [`9fc3e33`](https://github.com/rippleFCL/bws-cache/commit/9fc3e3356105af3e9f4b163e634fb4de51cb62ab) - fix type issues *(commit by [@rippleFCL](https://github.com/rippleFCL))*
- [`bd574b5`](https://github.com/rippleFCL/bws-cache/commit/bd574b524c94f0a64d401ed99e2935b15dd89eaa) - **deps**: update dependency prometheus-client to ^0.22.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`9911a17`](https://github.com/rippleFCL/bws-cache/commit/9911a179831e21524cd2b8d5d23f4eea6b4714d4) - remove exceptions for deprecated `ORG_ID` *(commit by [@tigattack](https://github.com/tigattack))*
- [`bdad4d2`](https://github.com/rippleFCL/bws-cache/commit/bdad4d2ef3d32e77801c81ba660f05775a8a12ee) - **ansible_collection**: remove deprecated header *(commit by [@tigattack](https://github.com/tigattack))*
- [`66c3733`](https://github.com/rippleFCL/bws-cache/commit/66c3733f413cca2412f9fefdf1cd5de961f8fdbe) - **dockerfile**: remove deprecated env var *(commit by [@tigattack](https://github.com/tigattack))*
- [`cb20f5d`](https://github.com/rippleFCL/bws-cache/commit/cb20f5d83a70b3dec830ce96be1c40f612bd27c0) - **deps**: update dependency uvicorn to ^0.35.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`900379c`](https://github.com/rippleFCL/bws-cache/commit/900379c202ad2d77bbef4f4a417846c26b8795e9) - **deps**: update dependency fastapi to ^0.116.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*

### :wrench: Chores
- [`f051931`](https://github.com/rippleFCL/bws-cache/commit/f051931424a2be0752ef732ed8d053733cc130f7) - **deps**: update stefanzweifel/git-auto-commit-action action to v6 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`9c5d7b9`](https://github.com/rippleFCL/bws-cache/commit/9c5d7b9ccc425bf0a104b9bcb3872b00849a1b45) - bump python version in lint pipeline *(commit by [@rippleFCL](https://github.com/rippleFCL))*
- [`12281a4`](https://github.com/rippleFCL/bws-cache/commit/12281a473a2654748edef356a3b33375b8f4baf2) - formating *(commit by [@rippleFCL](https://github.com/rippleFCL))*
- [`10b7621`](https://github.com/rippleFCL/bws-cache/commit/10b76214742e6c40b792db4da79270821363fb40) - enable additional Ruff rules *(commit by [@tigattack](https://github.com/tigattack))*
- [`c1dac22`](https://github.com/rippleFCL/bws-cache/commit/c1dac22db53173ba600897590cf22df18c63224b) - remove type ignore *(commit by [@rippleFCL](https://github.com/rippleFCL))*
- [`fbaf085`](https://github.com/rippleFCL/bws-cache/commit/fbaf0857fda514e74050bd56b3c16e032e136541) - **deps**: update dependency ruff to ^0.12.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`bb83b51`](https://github.com/rippleFCL/bws-cache/commit/bb83b51859cf71db4e1d83624f3c00e6f86b0b44) - **ansible_collection**: bump version *(commit by [@tigattack](https://github.com/tigattack))*


## [server-v2.6.1] - 2025-05-09
### :sparkles: New Features
- [`34e5883`](https://github.com/rippleFCL/bws-cache/commit/34e5883e1b3b0c327d0ab43b6610b5e48e51e6cf) - **dockerfile**: make the container rootless

### :wrench: Chores
- [`6bb3192`](https://github.com/rippleFCL/bws-cache/commit/6bb31923185e5443ef3bccac3095f92f0b55b05f) - **galaxy.yml**: bump ansible galaxy version
- [`a2b84c0`](https://github.com/rippleFCL/bws-cache/commit/a2b84c0e3f89ec7a3e5e536b8967f9741b41a8c2) - **CHANGELOG.md**: update ansible changelog
- [`a8c18e3`](https://github.com/rippleFCL/bws-cache/commit/a8c18e3637932c45b053137c5e1541e6ac593064) - **deps**: update dependency ruff to v0.11.9 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*


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
[server-v2.6.1]: https://github.com/rippleFCL/bws-cache/compare/server-v2.6.0...server-v2.6.1
[server-v3.0.0]: https://github.com/rippleFCL/bws-cache/compare/ansible-v1.2.1...server-v3.0.0
