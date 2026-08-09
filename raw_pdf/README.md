# Raw PDF corpus

The three PDFs below are the locked source documents for the PANDA research QA
corpus. They are intentionally excluded from Git because they are large,
user-provided inputs. **用户自行提供，不纳入Git。** Keep this README tracked so
that a checkout still documents the required inputs and their byte-level
identity.

| 文件 | SHA-256 | 用途 |
| --- | --- | --- |
| `thesis.pdf` | `9930dfd79c74b9d1dadc6d1eb6c093ac10ccb45e12f641887bcdc8b823b8690a` | Luminosity Determination with Restgas Background from the Target for the PANDA Experiment（主论文） |
| `Diss_2015_Karavdina_Anastasia.pdf` | `422421852c5a046c24e894a77b9380988ec8172914e9b30b055a100145c07a2b` | Preparation for the Accurate Luminosity Measurement by Antiproton-Proton Elastic Scattering |
| `Diss_2017_Pflueger_Stefan.pdf` | `1b6ec987fc1430be085f2a7ba631d634f6580115ff0a90dff090dfcba5e990f3` | Precise Determination of the Luminosity with the PANDA-Luminosity-Detector |

## Provision and verification

Place the three files in this directory yourself, then verify their SHA-256
digests from the `PANDA_Agent` directory:

```powershell
Get-FileHash -Algorithm SHA256 raw_pdf\thesis.pdf
Get-FileHash -Algorithm SHA256 raw_pdf\Diss_2015_Karavdina_Anastasia.pdf
Get-FileHash -Algorithm SHA256 raw_pdf\Diss_2017_Pflueger_Stefan.pdf
```

The reported hashes must match the table above and the locked entries in
`configs/corpora.yaml` and `data/manifests/source_manifest.json` before corpus
ingestion. Do not add the PDF bytes to Git.
