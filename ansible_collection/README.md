# Ansible Collection - [ripplefcl.bwscache](https://galaxy.ansible.com/ui/repo/published/ripplefcl/bwscache)

[![Build Status][build_badge]][build_link]

This collection provides a lookup plugin for querying bws-cache.

## Installation

```
ansible-galaxy collection install ripplefcl.bwscache
```

## Usage

**Lookup secret by ID:**

```yml
- name: Get secret
  ansible.builtin.debug:
    msg: "{{ lookup('ripplefcl.bwscache.secret', '01fae166-302b-4e75-b7a4-c6887ef7e3a8') }}"

# Returns: "{"id": "01fae166-302b-4e75-b7a4-c6887ef7e3a8", "key": "my_secret_key", "value": "my_secret_value"}"
```

**Lookup secret by key:**

```yml
- name: Get secret
  ansible.builtin.debug:
    msg: "{{ lookup('ripplefcl.bwscache.secret', 'my_secret_key') }}"

# Returns: "{"id": "01fae166-302b-4e75-b7a4-c6887ef7e3a8", "key": "my_secret_key", "value": "my_secret_value"}"
```

**Lookup secret by key, returning only the secret value:**

```yml
- name: Get secret
  ansible.builtin.debug:
    msg: "{{ lookup('ripplefcl.bwscache.secret', 'my_secret_key').value }}"

# Returns: "my_secret_value"
```

[build_badge]:  https://img.shields.io/github/actions/workflow/status/rippleFCL/bws-cache/ansible.yml?branch=main&label=Ansible%20Lint
[build_link]:   https://github.com/rippleFCL/bws-cache/actions/workflows/ansible.yml
