# Makefile used for automatically generating kubernetes manifests...

# Set the k3s kubeconfig file (it should be the server-side kubeconfig!)
KUBECONFIG=/etc/rancher/k3s/k3s.yaml

NAMESPACE=gleam-playground
XNAMESPACES=openfaas-fn

# Set the output directory for all generated manifests
OUTPUT_DIR=manifests

ROOT_DIR=settings

# Set service settings files
GLEAM_PLAYGROUND_SETTINGS=$(ROOT_DIR)/gleam-playground-settings.conf

manifests-gleam-playground:
	python k8smanifests.py \
	--config_file $(GLEAM_PLAYGROUND_SETTINGS) \
	--service_name gleam-playground \
	--kubeconfig $(KUBECONFIG) \
	--output_dir $(OUTPUT_DIR) \
	--namespace $(NAMESPACE) \
	--xnamespaces $(XNAMESPACES)

manifests-redis:
	python k8smanifests.py \
	--config_file $(GLEAM_PLAYGROUND_SETTINGS) \
	--service_name redis \
	--kubeconfig $(KUBECONFIG) \
	--output_dir $(OUTPUT_DIR) \
	--namespace $(NAMESPACE)

all-manifests: manifests-gleam-playground manifests-redis

apply-manifests:
	sudo k3s kubectl apply -f $(manifests)/.

build-frontend:
	python build.py \
	--user nicklasxyz \
	--version latest \
	--settings settings \
	--service frontend \
	--action build

push-frontend:
	python build.py \
	--user nicklasxyz \
	--version latest \
	--settings settings \
	--service frontend \
	--action push
