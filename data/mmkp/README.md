# MMKP benchmark instances (third-party data)

Source:
- **Instances.** I07–I13 (Khan et al., 2002) and INST01–INST20 (Hifi et al., 2004, 2006), as distributed by Chen & Hao (2014) at https://leria-info.univ-angers.fr/~jinkao.hao/mmkp.html (`download/ClassicINST.zip`, unpacked in `ClassicINST/`).
- **Certificates.** The solution certificates with the best known values are in `certificates/`, from the links on the same page.

These files belong to their original authors. They are included unchanged so the results can be reproduced, and the MIT license of this repository does not apply to them. `src/mmkp.py` reads them and verifies every certificate.
