SOURCE_DIR = ./src
BUILD_DIR = ./bin

${BUILD_DIR}/supercam.py: ${wildcard ${SOURCE_DIR}/*.py} ${SOURCE_DIR}/main.py
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)
	head -n 1 ${SOURCE_DIR}/main.py >> $@
	echo >> $@
	grep -h ^import $^ | sort -u >> $@
	echo >> $@
	grep -hv -e ^#! -e import $^ >> $@
	echo >> $@
	chmod +x $@

run: ${BUILD_DIR}/supercam.py
	${BUILD_DIR}/supercam.py

clean:
	rm -rf $(BUILD_DIR)