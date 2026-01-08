FILEMGR_WEB_VERSION = 1.0
FILEMGR_WEB_SITE = $(TOPDIR)/package/filemgr_web
FILEMGR_WEB_SITE_METHOD = local
FILEMGR_WEB_LICENSE = MIT
FILEMGR_WEB_DEPENDENCIES = python3

define FILEMGR_WEB_BUILD_CMDS
    # Nothing to build
endef

define FILEMGR_WEB_INSTALL_TARGET_CMDS
    # Install Python script (0644, no execute)
    $(INSTALL) -D -m 0644 $(@D)/src/filemgr_web.py $(TARGET_DIR)/usr/bin/filemgr_web.py
    # Install icons into /files/icons (0644)
    $(INSTALL) -D -m 0644 $(@D)/src/icons/folder.png $(TARGET_DIR)/files/icons/folder.png
    $(INSTALL) -D -m 0644 $(@D)/src/icons/textfile.png $(TARGET_DIR)/files/icons/textfile.png
    $(INSTALL) -D -m 0644 $(@D)/src/icons/image.png $(TARGET_DIR)/files/icons/image.png
    $(INSTALL) -D -m 0644 $(@D)/src/icons/pdf.png $(TARGET_DIR)/files/icons/pdf.png
endef

$(eval $(generic-package))

