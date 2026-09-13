import mdadm_matrix

mdadm_matrix.APP_VERSION = "1.61"
mdadm_matrix.APP_TITLE = f"MDADM Manager v{mdadm_matrix.APP_VERSION} // MATRIX ROOT"

from mdadm_matrix.app import MdadmManager
from mdadm_matrix.rebuild_ui import installer_progression_rebuild

installer_progression_rebuild(MdadmManager)

from mdadm_matrix.main import main

if __name__ == "__main__":
    main()
