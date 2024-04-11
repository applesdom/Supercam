SOURCE_DIR = ./src
BUILD_DIR = ./bin

supercam.py:
	mkdir -p $(BUILD_DIR)
	cp "$(SOURCE_DIR)/main.py" "$(BUILD_DIR)/supercam.py"

clean:
	rm -rf $(BUILD_DIR)