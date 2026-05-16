import csv, io

with open(r'data\golden_dataset.csv', encoding='utf-8', newline='') as f:
    content = f.read()

reader = csv.DictReader(io.StringIO(content))
fieldnames = reader.fieldnames
rows = list(reader)

def add_variants(row, new_variants):
    existing = row.get('expected_allowed_variants', '').strip()
    existing_list = [v.strip() for v in existing.split('|') if v.strip()] if existing else []
    existing_upper = {v.upper() for v in existing_list}
    for v in new_variants:
        if v.strip().upper() not in existing_upper:
            existing_list.append(v.strip())
            existing_upper.add(v.strip().upper())
    row['expected_allowed_variants'] = '|'.join(existing_list)

# ── A1: Arabic name variant families ──────────────────────────────────────────
A1 = {
    'KYC001': ['Mohamed Ali Hassan', 'Mohamed Ali Hasan', 'Mohammed Ali Hasan'],
    'KYC002': ['Abdallah Muhammad', 'Abdallah Mohamed', 'Abd Allah Muhammad'],
    'KYC004': ['Abou Muhammad Al-Julani', 'Abu Muhammad Aljulani', 'Abu Muhammad El Julani', 'Abou Mohammed Al Julani'],
    'KYC005': ['Mohamed Hassan Ali', 'Mohammad Hassan Ali', 'Mohammed Hasan Ali', 'Mohamed Hasan Ali', 'Muhammad Hassan Ali'],
    'KYC028': ['Hassan Ali Mohammad', 'Hasan Ali Mohammed', 'Hasan Ali Mohamed', 'Hassan Ali Mohamed'],
    'IMG006': ['Ahmed Abdel Nassar', 'Ahmed Samir Nasr Abdel Naser', 'Ahmed Samir Nasr Abdul Naser'],
    'IMG007': ['Nihad Ibrahim El-Sayed Al-Naggar', 'Nihad Ibrahim Elsayyed Alnaggar', 'Nihad Ibrahim El Sayyed Al Naggar'],
    'KYC031': ['Khalid Abdul Rahman Salih', 'Khaled Abdulrahman Saleh', 'Khaled Abdulrahman Salih'],
    'KYC032': ['Fatema Al Zahra Ali', 'Fatimah El Zahra Ali', 'Fatimah Al-Zahra Ali', 'Fatima El Zahra Ali'],
    'KYC034': ['Ibn Salem Al-Kaabi', 'Bin Salem Al Kaabi', 'Ibn Salim Al Kaabi', 'Bin Salem Al-Kaabi'],
    'KYC039': ['Abdul-Majeed Al Harbi', 'Abdulmajid Al Harbi', 'Abdul Majeed Al Harbi', 'Abdel-Majid Al Harbi'],
}
# Rows with Arabic script in variants field — overwrite entirely with clean Latin
A1_OVERWRITE = {
    'KYC033': 'Youssef Abdel Aziz Mahmud|Yousuf Abdelaziz Mahmood|Yousef Abdelaziz Mahmoud|Yusuf Abdel Aziz Mahmoud|Yousuf Abdel Aziz Mahmoud',
    'KYC040': 'Mariam Hassan Youssef|Maryam Hassan Yousuf|Mariam Hasan Youssef|Maryam Hasan Youssef|Mariam Hasan Yusuf',
}

# ── A2: Address punctuation / suffix variants ──────────────────────────────────
A2 = {
    'KYC003':  ['SHEIKH ZAYED RD DUBAI', 'Sheikh Zayed Road Dubai', 'Sheikh Zayed Street Dubai'],
    'KYC010':  ['Tokyo Shinjuku-ku', 'Shinjuku-ku Tokyo', 'Tokyo Shinjuku Ku', 'Shinjuku Tokyo'],
    'KYC015':  ['Lenina St 10 Moscow', '10 Lenina Street Moscow', '10 Lenina St Moscow', 'Ulitsa Lenina 10 Moscow'],
    'KYC019':  ['88 Jianguo Road Chaoyang District Beijing', '88 Jianguo Road, Chaoyang District, Beijing', '88 Jianguo Road Chaoyang Beijing'],
    'IMG003':  ['Tokyo Japan'],
    'KYC023':  ['Kifisias Ave 10 Athens', 'Kifisias Avenue 10, Athens'],
    'KYC036':  ['Block 3 Street 12 Kuwait City', 'Block 3, Street 12, Kuwait City', 'Block 3 St 12 Kuwait City', 'Kuwait City Block 3 Street 12'],
    'KYC054':  ['Mira Ave 25 Saint Petersburg', 'Mira Avenue 25 St Petersburg', 'Mira Prospekt 25 Saint Petersburg'],
    'KYC064':  ['100 Century Avenue Pudong New Area Shanghai', '100 Century Avenue, Pudong New Area, Shanghai', '100 Century Ave Pudong Shanghai'],
    'KYC069':  ['18 Tiyu East Road Tianhe District Guangzhou', '18 Tiyu East Road, Tianhe District, Guangzhou', '18 Tiyu East Rd Tianhe Guangzhou'],
    'KYC073':  ['Stadiou St 15 Athens', '15 Stadiou Street Athens'],
    'KYC089':  ['100 Songren Road Xinyi District Taipei', '100 Songren Road, Xinyi District, Taipei', '100 Songren Rd Xinyi Taipei'],
    'KYC090':  ['27 Zhongguancun Street Haidian District Beijing', '27 Zhongguancun Street, Haidian District, Beijing', '27 Zhongguancun St Haidian Beijing'],
    'IMG013':  ['Kifisias Ave 30', '30 Kifisias Avenue'],
}

# ── A3: Japanese long-vowel OO completeness ────────────────────────────────────
A3 = {
    'KYC006':  ['YAMADA TAROO', 'TAROO YAMADA'],
    'KYC029':  ['TAKAHASHI ICHIROO', 'ICHIROO TAKAHASHI'],
    'KYC041':  ['SUZUKI ICHIROO', 'ICHIROO SUZUKI'],
    'KYC042':  ['KOOICHI ITO', 'ITO KOOICHI', 'KOUICHI ITO'],
    'KYC046':  ['NAKAMURA SHOO', 'SHOO NAKAMURA'],
    'KYC047':  ['WATANABE KOOICHI', 'KOOICHI WATANABE', 'KOUICHI WATANABE'],
    'IMG016':  ['NITO SHINJI', 'SHINJI NITO', 'NITOU SHINJI', 'SHINJI NITOU', 'NITOO SHINJI', 'SHINJI NITOO'],
}

for row in rows:
    cid = row['case_id']
    if cid in A1:
        add_variants(row, A1[cid])
    if cid in A1_OVERWRITE:
        row['expected_allowed_variants'] = A1_OVERWRITE[cid]
    if cid in A2:
        add_variants(row, A2[cid])
    if cid == 'KYC035':
        # Fix Arabic chars in expected_english + set clean variants
        row['expected_english'] = 'King Faisal Street, Manama'
        row['expected_allowed_variants'] = 'King Faisal Street Manama|King Faisal St Manama|King Faisal Road Manama'
    if cid in A3:
        add_variants(row, A3[cid])

out = io.StringIO()
writer = csv.DictWriter(out, fieldnames=fieldnames, lineterminator='\n')
writer.writeheader()
writer.writerows(rows)

with open(r'data\golden_dataset.csv', encoding='utf-8', newline='', mode='w') as f:
    f.write(out.getvalue())

print(f'Written {len(rows)} rows.')
for row in rows:
    cid = row['case_id']
    if cid in ('KYC001', 'KYC010', 'KYC033', 'KYC035', 'KYC040', 'IMG016'):
        v = row['expected_allowed_variants']
        print(f"  {cid}: {v[:110]}")
        if cid == 'KYC035':
            print(f"    english={row['expected_english']}")
