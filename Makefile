SOURCE_DIR = ./src
BUILD_DIR = ./bin

${BUILD_DIR}/supercam.py: ${wildcard ${SOURCE_DIR}/*.py} ${SOURCE_DIR}/main.py
	mkdir -p $(BUILD_DIR)
	head -n 1 ${SOURCE_DIR}/main.py >> $@
	echo >> $@
	grep -h ^import $^ | sort -u >> $@
	echo >> $@
	grep -hv -e ^#! -e import $^ >> $@
	echo >> $@
	chmod +x $@

clean:
	rm -rf $(BUILD_DIR)