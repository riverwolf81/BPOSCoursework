################################################################################
# Filebrowser Buildroot Package
################################################################################

FILEBROWSER_VERSION = 2.51.0
FILEBROWSER_SITE = $(TOPDIR)/package/filebrowser/src
FILEBROWSER_SITE_METHOD = local
FILEBROWSER_LICENSE = MIT
FILEBROWSER_LICENSE_FILES = LICENSE

define FILEBROWSER_INSTALL_TARGET_CMDS
    #Copy filebrowser to target
    cp $(@D)/filebrowser $(TARGET_DIR)/usr/bin/filebrowser
endef

$(eval $(generic-package))

