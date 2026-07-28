$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$masterPath = Join-Path $PSScriptRoot 'literature_master.csv'
$bibPath = Join-Path $PSScriptRoot 'library.bib'
$replacementLogPath = Join-Path $PSScriptRoot 'reference_replacement_log.csv'

$removedKeys = @(
    'manning1997semiconductor',
    'qin2017snr',
    'lu2017temperature',
    'wang2019comprehensive',
    'young1981design',
    'cassioli2000simulator',
    'dorren2004logic',
    'sun2006gain',
    'zilkie2007carrier',
    'zilkie2008linewidth',
    'devries2015pulse',
    'wu2015separation',
    'pastorgraells2016single',
    'liu2016distributed',
    'he2017multievent',
    'muanenda2018dynamic',
    'xue2018phase',
    'lu2020snr'
)

$newRows = @(
    [ordered]@{
        record_id='LIT076'; title='相位敏感光时域反射分布式光纤传感技术'; authors='张旭幸; 丁哲文; 洪瑞; 陈晓红; 梁蕾; 张驰; 王峰; 邹宁睿; 张益昕'; year='2021'; document_type='journal article'; journal_or_conference='光学学报'; volume_issue_pages='41(1):0106004'; doi='10.3788/AOS202141.0106004'; stable_url='https://doi.org/10.3788/AOS202141.0106004'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T1'; secondary_tags='phi-OTDR review; system architecture; applications'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='zhang2021phase_cn'; chap1_use='Chinese review of phi-OTDR principles and development'; chap2_use='system architecture and principle'; claim_ids='C01;C04'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT077'; title='基于Φ-OTDR的光纤分布式传感信号处理及应用'; authors='吴慧娟; 刘欣雨; 饶云江'; year='2021'; document_type='journal article'; journal_or_conference='激光与光电子学进展'; volume_issue_pages='58(13):1306003'; doi='10.3788/LOP202158.1306003'; stable_url='https://doi.org/10.3788/LOP202158.1306003'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T4'; secondary_tags='signal processing; event recognition; DAS applications'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='wu2021processing_cn'; chap1_use='Chinese progress in DAS signal processing'; chap2_use='signal processing framework'; claim_ids='C03;C04'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT078'; title='基于MEEMD-HHT的分布式光纤振动传感系统信号特征提取方法'; authors='于淼; 张耀鲁; 徐泽辰; 何禹潼'; year='2021'; document_type='journal article'; journal_or_conference='红外与激光工程'; volume_issue_pages='50(7):20210223'; doi='10.3788/IRLA20210223'; stable_url='https://doi.org/10.3788/IRLA20210223'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T4'; secondary_tags='MEEMD-HHT; feature extraction; vibration signal processing'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='yu2021meemd_cn'; chap1_use='domestic signal-processing example'; chap2_use='feature extraction method'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT079'; title='相位敏感光时域反射仪的信号处理方法综述'; authors='田曼伶; 刘东辉; 曹晓敏; 余贶琭'; year='2021'; document_type='journal article'; journal_or_conference='光学精密工程'; volume_issue_pages='29(9):2189-2209'; doi='10.37188/OPE.20212909.2189'; stable_url='https://doi.org/10.37188/OPE.20212909.2189'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T4'; secondary_tags='signal processing review; denoising; feature extraction; machine learning'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='tian2021signal_cn'; chap1_use='Chinese review of phi-OTDR signal processing'; chap2_use='processing-method classification'; claim_ids='C03;C04'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT080'; title='光纤分布式声传感的动态范围扩展方法研究'; authors='马喆; 王逸璇; 江俊峰; 王双; 张建德; 杨宁; 徐天华; 丁振扬; 刘铁根'; year='2021'; document_type='journal article'; journal_or_conference='光学学报'; volume_issue_pages='41(13):1306008'; doi='10.3788/AOS202141.1306008'; stable_url='https://doi.org/10.3788/AOS202141.1306008'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T1'; secondary_tags='dynamic range; LFM pulse; sideband modulation'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='ma2021dynamic_cn'; chap1_use='domestic dynamic-range extension'; chap2_use='frequency-time mapping and dynamic range'; claim_ids='C01'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT081'; title='相位敏感光时域反射系统低频响应性能优化'; authors='于淼; 孙铭阳; 何禹潼; 张崇富; 郑志丰; 孔谦'; year='2022'; document_type='journal article'; journal_or_conference='红外与激光工程'; volume_issue_pages='51(5):20211125'; doi='10.3788/IRLA20211125'; stable_url='https://doi.org/10.3788/IRLA20211125'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T3'; secondary_tags='AOM; common clock; low-frequency response; phase noise'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='yu2022lowfrequency_cn'; chap1_use='AOM and synchronous-clock progress'; chap2_use='AOM clock and phase-noise model'; claim_ids='C02;C03'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT082'; title='光纤分布式声传感系统在GIS耐压测试中的应用'; authors='黄涛; 孙恒东; 蒋骏; 王章轩; 杨永前; 陈金林'; year='2023'; document_type='journal article'; journal_or_conference='激光技术'; volume_issue_pages='47(4):459-462'; doi='10.7510/jgjs.issn.1001-3806.2023.04.003'; stable_url='https://doi.org/10.7510/jgjs.issn.1001-3806.2023.04.003'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T5'; secondary_tags='DAS application; GIS; fault location'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='huang2023gis_cn'; chap1_use='domestic engineering application'; chap2_use=''; claim_ids='C01'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT083'; title='基于宽带声光调制的高保真相位敏感光时域反射计系统'; authors='雷艳阳; 姜桃飞; 马云宾; 夏猛; 汤晓惠; 隋景林; 杨芳; 杜学新; 董永康'; year='2024'; document_type='journal article'; journal_or_conference='光学学报'; volume_issue_pages='44(1):0106017'; doi='10.3788/AOS231426'; stable_url='https://doi.org/10.3788/AOS231426'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T3'; secondary_tags='broadband AOM; multifrequency pulse; coherent fading'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='lei2024broadband_cn'; chap1_use='recent domestic AOM and fading-control work'; chap2_use='multi-frequency AOM modulation'; claim_ids='C02;C03'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT084'; title='基于改进奇异值分解法降噪的频分复用Φ-OTDR'; authors='陈娟; 张红娟; 王鹏飞; 高妍; 靳宝全'; year='2024'; document_type='journal article'; journal_or_conference='中国激光'; volume_issue_pages='51(22):2210003'; doi='10.3788/CJL240638'; stable_url='https://doi.org/10.3788/CJL240638'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T4'; secondary_tags='frequency division multiplexing; SVD; noise suppression'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='chen2024svd_cn'; chap1_use='recent domestic noise-suppression work'; chap2_use='signal denoising example'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT085'; title='Ф-OTDR系统中的衰落效应抑制研究进展（特邀）'; authors='雷艳阳; 陈金博; 刘帅旗; 李天夫; 董永康'; year='2025'; document_type='journal article'; journal_or_conference='红外与激光工程'; volume_issue_pages='54(4):20250051'; doi='10.3788/IRLA20250051'; stable_url='https://doi.org/10.3788/IRLA20250051'; metadata_source='journal official page and full text'; search_id='S006'; primary_theme='T4'; secondary_tags='fading review; polarization diversity; coherent fading'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='official Chinese full text verified'; include_status='include'; exclusion_reason=''; bibkey='lei2025fading_cn'; chap1_use='recent Chinese review of fading suppression'; chap2_use='polarization and coherent fading'; claim_ids='C03;C04'; metadata_verified_at='2026-07-27'; publication_language='zh'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT086'; title='Semiconductor optical amplifiers: recent advances and applications'; authors='Aneesh Sobhanan; Aravind Anthur; Sean O-Duill; Mark Pelusi; Shu Namiki; Liam Barry; Deepa Venkitesh; Govind P. Agrawal'; year='2022'; document_type='journal article'; journal_or_conference='Advances in Optics and Photonics'; volume_issue_pages='14(3):571-651'; doi='10.1364/AOP.451872'; stable_url='https://doi.org/10.1364/AOP.451872'; metadata_source='publisher official page and DOI metadata'; search_id='S007'; primary_theme='T2'; secondary_tags='SOA review; carrier dynamics; gain saturation; coherent signals'; domestic_or_international='international'; evidence_level='A'; fulltext_status='publisher abstract and accepted manuscript metadata verified'; include_status='include'; exclusion_reason=''; bibkey='sobhanan2022soa'; chap1_use='recent SOA mechanism review'; chap2_use='SOA carrier and gain model'; claim_ids='C02'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT087'; title='Dynamic power and chirp measurements of a quantum dash semiconductor optical amplifier amplified picosecond pulses using a linear pulse characterization technique'; authors='Michael J. Connelly; Javier Romero-Vivas; Pascal Morel; Ammar Sharaiha; Frédéric Pommereau; Catherine Fortin'; year='2023'; document_type='journal article'; journal_or_conference='Optical and Quantum Electronics'; volume_issue_pages='55(1):36'; doi='10.1007/s11082-022-04301-7'; stable_url='https://doi.org/10.1007/s11082-022-04301-7'; metadata_source='DOI metadata and university repository'; search_id='S007'; primary_theme='T2'; secondary_tags='SOA chirp; dynamic power; pulse characterization'; domestic_or_international='international'; evidence_level='A'; fulltext_status='repository abstract and DOI metadata verified'; include_status='include'; exclusion_reason=''; bibkey='connelly2023dynamic'; chap1_use='recent SOA pulse-chirp evidence'; chap2_use='SOA transient chirp model'; claim_ids='C02'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT088'; title='A Novel φ-OTDR System With a Phase Demodulation Module Based on Sagnac Balanced Interferometer'; authors='Xiang Zhong; Baofei Zhang; Jie Ren; Huaxia Deng; Xiaoshan Chen; Mengchao Ma'; year='2021'; document_type='journal article'; journal_or_conference='Journal of Lightwave Technology'; volume_issue_pages='39(22):7307-7314'; doi='10.1109/JLT.2021.3113082'; stable_url='https://doi.org/10.1109/JLT.2021.3113082'; metadata_source='DOI metadata and publisher page'; search_id='S007'; primary_theme='T4'; secondary_tags='Sagnac balanced interferometer; phase demodulation'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='publisher abstract and DOI metadata verified'; include_status='include'; exclusion_reason=''; bibkey='zhong2021sagnac'; chap1_use='recent phase-demodulation architecture'; chap2_use='complex phase extraction'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT089'; title='Characterizing detection noise in phase-sensitive optical time domain reflectometry'; authors='Xin Lu; Katerina Krebber'; year='2021'; document_type='journal article'; journal_or_conference='Optics Express'; volume_issue_pages='29(12):18791-18806'; doi='10.1364/OE.424410'; stable_url='https://doi.org/10.1364/OE.424410'; metadata_source='DOI metadata and publisher page'; search_id='S007'; primary_theme='T4'; secondary_tags='detection noise; phase stability; SNR'; domestic_or_international='international'; evidence_level='A'; fulltext_status='publisher abstract and DOI metadata verified'; include_status='include'; exclusion_reason=''; bibkey='lu2021detection'; chap1_use='recent detection-noise evidence'; chap2_use='phase-noise and SNR model'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT090'; title='Phase error analysis and unwrapping error suppression in phase-sensitive optical time domain reflectometry'; authors='Xin Lu; Katerina Krebber'; year='2022'; document_type='journal article'; journal_or_conference='Optics Express'; volume_issue_pages='30(5):6934-6948'; doi='10.1364/OE.446517'; stable_url='https://doi.org/10.1364/OE.446517'; metadata_source='DOI metadata and publisher page'; search_id='S007'; primary_theme='T4'; secondary_tags='phase error; phase unwrapping; low SNR'; domestic_or_international='international'; evidence_level='A'; fulltext_status='publisher abstract and DOI metadata verified'; include_status='include'; exclusion_reason=''; bibkey='lu2022phaseerror'; chap1_use='recent phase-error evidence'; chap2_use='unwrapping-error analysis'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT091'; title='Digitalized phase demodulation scheme of φ-OTDR based on cross-coherence between Rayleigh back-scattering beat signals'; authors='Yang Yang; An Sun; Ting Fan; Qi Li'; year='2022'; document_type='journal article'; journal_or_conference='Optical Fiber Technology'; volume_issue_pages='71:102896'; doi='10.1016/j.yofte.2022.102896'; stable_url='https://doi.org/10.1016/j.yofte.2022.102896'; metadata_source='DOI metadata and publisher page'; search_id='S007'; primary_theme='T4'; secondary_tags='digital phase demodulation; cross coherence; beat signal'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='publisher abstract and DOI metadata verified'; include_status='include'; exclusion_reason=''; bibkey='yang2022digitalized'; chap1_use='recent digital phase-demodulation work'; chap2_use='complex beat-signal demodulation'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT092'; title='Mitigating the Impact of Frequency Drift on Φ-OTDR Demodulation With WOA-VMD'; authors='Lijuan Zhao; Xuzhe Zhang; Zhiniu Xu'; year='2024'; document_type='journal article'; journal_or_conference='IEEE Photonics Technology Letters'; volume_issue_pages='36(1):31-34'; doi='10.1109/LPT.2023.3335042'; stable_url='https://doi.org/10.1109/LPT.2023.3335042'; metadata_source='DOI metadata and publisher page'; search_id='S007'; primary_theme='T4'; secondary_tags='frequency drift; demodulation; WOA-VMD'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='publisher abstract and DOI metadata verified'; include_status='include'; exclusion_reason=''; bibkey='zhao2024frequency'; chap1_use='recent frequency-drift compensation'; chap2_use='frequency mismatch and demodulation'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    },
    [ordered]@{
        record_id='LIT093'; title='Noise Performance Analysis and Optimization of Downsampling Heterodyne Φ-OTDR'; authors='Guo Zhu; Fei Liu; Xiaojun Liu; Santosh Kumar; Xian Zhou'; year='2024'; document_type='journal article'; journal_or_conference='IEEE Sensors Journal'; volume_issue_pages='24(9):14093-14100'; doi='10.1109/JSEN.2024.3368227'; stable_url='https://doi.org/10.1109/JSEN.2024.3368227'; metadata_source='DOI metadata and publisher page'; search_id='S007'; primary_theme='T4'; secondary_tags='heterodyne phi-OTDR; downsampling; noise optimization'; domestic_or_international='domestic'; evidence_level='A'; fulltext_status='publisher abstract and DOI metadata verified'; include_status='include'; exclusion_reason=''; bibkey='zhu2024downsampling'; chap1_use='recent heterodyne-noise optimization'; chap2_use='sampling and noise model'; claim_ids='C03'; metadata_verified_at='2026-07-27'; publication_language='en'; recent_five_year='yes'
    }
)

$rows = Import-Csv -LiteralPath $masterPath
$removedRows = @($rows | Where-Object { $removedKeys -contains $_.bibkey })
$existingNewRows = @($rows | Where-Object { $newRows.bibkey -contains $_.bibkey })
if ($removedRows.Count -notin @(0, $removedKeys.Count)) {
    throw "Expected either 0 or $($removedKeys.Count) removable rows, found $($removedRows.Count)."
}

if ($removedRows.Count -eq $removedKeys.Count) {
    $retainedRows = @($rows | Where-Object { $removedKeys -notcontains $_.bibkey })
    $normalizedRetained = foreach ($row in $retainedRows) {
    [pscustomobject][ordered]@{
        record_id=$row.record_id
        title=$row.title
        authors=$row.authors
        year=$row.year
        document_type=$row.document_type
        journal_or_conference=$row.journal_or_conference
        volume_issue_pages=$row.volume_issue_pages
        doi=$row.doi
        stable_url=$row.stable_url
        metadata_source=$row.metadata_source
        search_id=$row.search_id
        primary_theme=$row.primary_theme
        secondary_tags=$row.secondary_tags
        domestic_or_international=$row.domestic_or_international
        evidence_level=$row.evidence_level
        fulltext_status=$row.fulltext_status
        include_status=$row.include_status
        exclusion_reason=$row.exclusion_reason
        bibkey=$row.bibkey
        chap1_use=$row.chap1_use
        chap2_use=$row.chap2_use
        claim_ids=$row.claim_ids
        metadata_verified_at=$row.metadata_verified_at
        publication_language='en'
        recent_five_year=$(if ([int]$row.year -ge 2021 -and [int]$row.year -le 2026) {'yes'} else {'no'})
    }
    }
    $combined = @($normalizedRetained) + @($newRows | ForEach-Object { [pscustomobject]$_ })
} elseif ($existingNewRows.Count -eq $newRows.Count) {
    $retainedRows = @($rows | Where-Object { $newRows.bibkey -notcontains $_.bibkey })
    $combined = @($rows)
} else {
    throw "Reference master is in an unexpected partially rebalanced state."
}

if ($combined.Count -ne 75) {
    throw "Expected 75 selected references after rebalancing, found $($combined.Count)."
}

$combined |
    Sort-Object @{Expression={[int]($_.record_id -replace '\D','')}} |
    Export-Csv -LiteralPath $masterPath -NoTypeInformation -Encoding UTF8

if ($removedRows.Count -eq $removedKeys.Count) {
    $replacementPairs = for ($i = 0; $i -lt $removedKeys.Count; $i++) {
        $old = $removedRows | Where-Object bibkey -eq $removedKeys[$i]
        $new = $newRows[$i]
        [pscustomobject][ordered]@{
            removed_bibkey=$old.bibkey
            removed_year=$old.year
            removed_title=$old.title
            replacement_bibkey=$new.bibkey
            replacement_year=$new.year
            replacement_title=$new.title
            reason='Rebalanced for Chinese-language coverage and 2021-2026 share; foundational sources retained separately where essential'
            audited_at='2026-07-27'
        }
    }
    $replacementPairs | Export-Csv -LiteralPath $replacementLogPath -NoTypeInformation -Encoding UTF8
}

$bib = Get-Content -LiteralPath $bibPath -Raw -Encoding UTF8
foreach ($key in @($removedKeys) + @($newRows.bibkey)) {
    $pattern = "(?ms)^@\w+\{$([regex]::Escape($key)),.*?(?=^@\w+\{|\z)"
    $bib = [regex]::Replace($bib, $pattern, '')
}

$newBib = @'

@article{zhang2021phase_cn,
  author  = {张旭幸 and 丁哲文 and 洪瑞 and 陈晓红 and 梁蕾 and 张驰 and 王峰 and 邹宁睿 and 张益昕},
  title   = {相位敏感光时域反射分布式光纤传感技术},
  journal = {光学学报},
  year    = {2021},
  volume  = {41},
  number  = {1},
  pages   = {0106004},
  doi     = {10.3788/AOS202141.0106004},
  url     = {https://doi.org/10.3788/AOS202141.0106004},
  language = {zh}
}

@article{wu2021processing_cn,
  author  = {吴慧娟 and 刘欣雨 and 饶云江},
  title   = {基于{$\Phi$-OTDR}的光纤分布式传感信号处理及应用},
  journal = {激光与光电子学进展},
  year    = {2021},
  volume  = {58},
  number  = {13},
  pages   = {1306003},
  doi     = {10.3788/LOP202158.1306003},
  url     = {https://doi.org/10.3788/LOP202158.1306003},
  language = {zh}
}

@article{yu2021meemd_cn,
  author  = {于淼 and 张耀鲁 and 徐泽辰 and 何禹潼},
  title   = {基于{MEEMD-HHT}的分布式光纤振动传感系统信号特征提取方法},
  journal = {红外与激光工程},
  year    = {2021},
  volume  = {50},
  number  = {7},
  pages   = {20210223},
  doi     = {10.3788/IRLA20210223},
  url     = {https://doi.org/10.3788/IRLA20210223},
  language = {zh}
}

@article{tian2021signal_cn,
  author  = {田曼伶 and 刘东辉 and 曹晓敏 and 余贶琭},
  title   = {相位敏感光时域反射仪的信号处理方法综述},
  journal = {光学精密工程},
  year    = {2021},
  volume  = {29},
  number  = {9},
  pages   = {2189--2209},
  doi     = {10.37188/OPE.20212909.2189},
  url     = {https://doi.org/10.37188/OPE.20212909.2189},
  language = {zh}
}

@article{ma2021dynamic_cn,
  author  = {马喆 and 王逸璇 and 江俊峰 and 王双 and 张建德 and 杨宁 and 徐天华 and 丁振扬 and 刘铁根},
  title   = {光纤分布式声传感的动态范围扩展方法研究},
  journal = {光学学报},
  year    = {2021},
  volume  = {41},
  number  = {13},
  pages   = {1306008},
  doi     = {10.3788/AOS202141.1306008},
  url     = {https://doi.org/10.3788/AOS202141.1306008},
  language = {zh}
}

@article{yu2022lowfrequency_cn,
  author  = {于淼 and 孙铭阳 and 何禹潼 and 张崇富 and 郑志丰 and 孔谦},
  title   = {相位敏感光时域反射系统低频响应性能优化},
  journal = {红外与激光工程},
  year    = {2022},
  volume  = {51},
  number  = {5},
  pages   = {20211125},
  doi     = {10.3788/IRLA20211125},
  url     = {https://doi.org/10.3788/IRLA20211125},
  language = {zh}
}

@article{huang2023gis_cn,
  author  = {黄涛 and 孙恒东 and 蒋骏 and 王章轩 and 杨永前 and 陈金林},
  title   = {光纤分布式声传感系统在{GIS}耐压测试中的应用},
  journal = {激光技术},
  year    = {2023},
  volume  = {47},
  number  = {4},
  pages   = {459--462},
  doi     = {10.7510/jgjs.issn.1001-3806.2023.04.003},
  url     = {https://doi.org/10.7510/jgjs.issn.1001-3806.2023.04.003},
  language = {zh}
}

@article{lei2024broadband_cn,
  author  = {雷艳阳 and 姜桃飞 and 马云宾 and 夏猛 and 汤晓惠 and 隋景林 and 杨芳 and 杜学新 and 董永康},
  title   = {基于宽带声光调制的高保真相位敏感光时域反射计系统},
  journal = {光学学报},
  year    = {2024},
  volume  = {44},
  number  = {1},
  pages   = {0106017},
  doi     = {10.3788/AOS231426},
  url     = {https://doi.org/10.3788/AOS231426},
  language = {zh}
}

@article{chen2024svd_cn,
  author  = {陈娟 and 张红娟 and 王鹏飞 and 高妍 and 靳宝全},
  title   = {基于改进奇异值分解法降噪的频分复用{$\Phi$-OTDR}},
  journal = {中国激光},
  year    = {2024},
  volume  = {51},
  number  = {22},
  pages   = {2210003},
  doi     = {10.3788/CJL240638},
  url     = {https://doi.org/10.3788/CJL240638},
  language = {zh}
}

@article{lei2025fading_cn,
  author  = {雷艳阳 and 陈金博 and 刘帅旗 and 李天夫 and 董永康},
  title   = {{$\Phi$-OTDR}系统中的衰落效应抑制研究进展（特邀）},
  journal = {红外与激光工程},
  year    = {2025},
  volume  = {54},
  number  = {4},
  pages   = {20250051},
  doi     = {10.3788/IRLA20250051},
  url     = {https://doi.org/10.3788/IRLA20250051},
  language = {zh}
}

@article{sobhanan2022soa,
  author  = {Sobhanan, Aneesh and Anthur, Aravind and O'Duill, Sean and Pelusi, Mark and Namiki, Shu and Barry, Liam and Venkitesh, Deepa and Agrawal, Govind P.},
  title   = {Semiconductor optical amplifiers: recent advances and applications},
  journal = {Advances in Optics and Photonics},
  year    = {2022},
  volume  = {14},
  number  = {3},
  pages   = {571--651},
  doi     = {10.1364/AOP.451872},
  url     = {https://doi.org/10.1364/AOP.451872}
}

@article{connelly2023dynamic,
  author  = {Connelly, Michael J. and Romero-Vivas, Javier and Morel, Pascal and Sharaiha, Ammar and Pommereau, Frédéric and Fortin, Catherine},
  title   = {Dynamic power and chirp measurements of a quantum dash semiconductor optical amplifier amplified picosecond pulses using a linear pulse characterization technique},
  journal = {Optical and Quantum Electronics},
  year    = {2023},
  volume  = {55},
  number  = {1},
  pages   = {36},
  doi     = {10.1007/s11082-022-04301-7},
  url     = {https://doi.org/10.1007/s11082-022-04301-7}
}

@article{zhong2021sagnac,
  author  = {Zhong, Xiang and Zhang, Baofei and Ren, Jie and Deng, Huaxia and Chen, Xiaoshan and Ma, Mengchao},
  title   = {A Novel {$\Phi$-OTDR} System With a Phase Demodulation Module Based on Sagnac Balanced Interferometer},
  journal = {Journal of Lightwave Technology},
  year    = {2021},
  volume  = {39},
  number  = {22},
  pages   = {7307--7314},
  doi     = {10.1109/JLT.2021.3113082},
  url     = {https://doi.org/10.1109/JLT.2021.3113082}
}

@article{lu2021detection,
  author  = {Lu, Xin and Krebber, Katerina},
  title   = {Characterizing detection noise in phase-sensitive optical time domain reflectometry},
  journal = {Optics Express},
  year    = {2021},
  volume  = {29},
  number  = {12},
  pages   = {18791--18806},
  doi     = {10.1364/OE.424410},
  url     = {https://doi.org/10.1364/OE.424410}
}

@article{lu2022phaseerror,
  author  = {Lu, Xin and Krebber, Katerina},
  title   = {Phase error analysis and unwrapping error suppression in phase-sensitive optical time domain reflectometry},
  journal = {Optics Express},
  year    = {2022},
  volume  = {30},
  number  = {5},
  pages   = {6934--6948},
  doi     = {10.1364/OE.446517},
  url     = {https://doi.org/10.1364/OE.446517}
}

@article{yang2022digitalized,
  author  = {Yang, Yang and Sun, An and Fan, Ting and Li, Qi},
  title   = {Digitalized phase demodulation scheme of {$\Phi$-OTDR} based on cross-coherence between Rayleigh back-scattering beat signals},
  journal = {Optical Fiber Technology},
  year    = {2022},
  volume  = {71},
  pages   = {102896},
  doi     = {10.1016/j.yofte.2022.102896},
  url     = {https://doi.org/10.1016/j.yofte.2022.102896}
}

@article{zhao2024frequency,
  author  = {Zhao, Lijuan and Zhang, Xuzhe and Xu, Zhiniu},
  title   = {Mitigating the Impact of Frequency Drift on {$\Phi$-OTDR} Demodulation With {WOA-VMD}},
  journal = {IEEE Photonics Technology Letters},
  year    = {2024},
  volume  = {36},
  number  = {1},
  pages   = {31--34},
  doi     = {10.1109/LPT.2023.3335042},
  url     = {https://doi.org/10.1109/LPT.2023.3335042}
}

@article{zhu2024downsampling,
  author  = {Zhu, Guo and Liu, Fei and Liu, Xiaojun and Kumar, Santosh and Zhou, Xian},
  title   = {Noise Performance Analysis and Optimization of Downsampling Heterodyne {$\Phi$-OTDR}},
  journal = {IEEE Sensors Journal},
  year    = {2024},
  volume  = {24},
  number  = {9},
  pages   = {14093--14100},
  doi     = {10.1109/JSEN.2024.3368227},
  url     = {https://doi.org/10.1109/JSEN.2024.3368227}
}
'@

$bib = $bib.TrimEnd() + "`r`n" + $newBib.Trim() + "`r`n"
[System.IO.File]::WriteAllText($bibPath, $bib, [System.Text.UTF8Encoding]::new($false))

Write-Host "Rebalanced reference library:"
Write-Host "  retained: $($retainedRows.Count)"
Write-Host "  removed:  $($removedRows.Count)"
Write-Host "  added:    $($newRows.Count)"
Write-Host "  total:    $($combined.Count)"
