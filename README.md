# LXC provision scripts

Provision an LXC (container or VM) from a .yaml file.

Run as:

    $> poetry run lxc-provision < priv/spec.yaml

## Example

Example spec.yaml:

    image: debian/bullseye
    vm: true  # optional
    secureboot: false  # optional
    name: my-project
    limits:
      memory: 1GB
    volumes:
      - name: my-project-directory
        src: ${HOME}/path/to/code
        dst: /root/path/to/code
    copy:
      - src: ${HOME}/.ssh/github.pub
        dst: /root/.ssh/id_rsa.pub
    setup_script:
      - apt update
