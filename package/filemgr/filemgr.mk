FILEMGR_VERSION = 1.0
FILEMGR_SITE = $(TOPDIR)/package/filemgr
FILEMGR_SITE_METHOD = local

FILEMGR_LICENSE = MIT
FILEMGR_DEPENDENCIES = sdl2 sdl2_ttf

define FILEMGR_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) \
		-I$(STAGING_DIR)/usr/include/SDL2 \
		$(@D)/src/filemgr.c \
		-o $(@D)/filemgr \
		`$(STAGING_DIR)/usr/bin/sdl2-config --cflags --libs` \
		-lSDL2_ttf
endef

define FILEMGR_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/filemgr \
		$(TARGET_DIR)/usr/bin/filemgr
endef

$(eval $(generic-package))

