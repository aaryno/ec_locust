# Dockerfile for quickly getting locust running
FROM ubuntu:17.10

WORKDIR /root
ADD update_distro.sh install_locust.sh requirements.txt ./
RUN ./update_distro.sh && ./install_locust.sh

ADD run_locust.sh wms_behavior.py wms_tester.py wms_256_tiles.csv ./
EXPOSE 8089
ENV URL http://localhost
CMD ["./run_locust.sh"]
