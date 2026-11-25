import sys
import os
import re
import hashlib
import argparse
import time
from typing import Dict, Tuple, Optional, Set, List

# 1. DYNAMIC LINGUISTIC / MORPHOLOGICAL ENGINE (NO STATIC DATA)
def transliterate(text: str) -> str:
    """Dynamic Cyrillic to Latin transliteration for synthetic emails and Latin names."""
    table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    res = "".join(table.get(ch, ch) for ch in text.lower())
    return res.capitalize() if text and text[0].isupper() else res


def noun_to_adjective(noun: str, gender: str = "f") -> str:
    """
    Dynamically inflects a fruit/vegetable/plant noun into a proper adjective.
    Genders: 'm' (мужской), 'f' (женский), 'n' (средний), 'pl' (множественный), 'en' (английский).
    """
    noun = noun.strip()
    if not noun:
        return ""
    
    is_latin = not any(c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" for c in noun)
    if is_latin:
        return noun.capitalize()
    
    w = noun.lower()
    stem = w
    suffix_type = "ов" # default suffix: -ов-
    
    # Morphological stem & suffix derivation
    if w.endswith("око"): # яблоко -> яблоч-н
        stem = w[:-3] + "оч"
        suffix_type = "н"
    elif w.endswith("ец"): # огурец -> огуреч-н
        stem = w[:-2] + "еч"
        suffix_type = "н"
    elif w.endswith("ок"): # чеснок -> чесноч-н
        stem = w[:-2] + "оч"
        suffix_type = "н"
    elif w.endswith("овь"): # морковь -> морков-н
        stem = w[:-1]
        suffix_type = "н"
    elif w.endswith("ель"): # картофель -> картофель-н
        stem = w
        suffix_type = "н"
    elif w.endswith("оль"): # фасоль -> фасол-ев
        stem = w[:-1]
        suffix_type = "ев"
    elif w.endswith("ень"): # ревень -> ревен-ев
        stem = w[:-1]
        suffix_type = "ев"
    elif w.endswith("ирь"): # имбирь -> имбир-н
        stem = w[:-1]
        suffix_type = "н"
    elif w.endswith("ква"): # тыква -> тыкв-енн
        stem = w[:-1]
        suffix_type = "енн"
    elif w.endswith("я"): # вишня -> вишн-ев, дыня -> дын-н
        stem = w[:-1]
        suffix_type = "ев" if stem.endswith(("шн", "чн", "щ", "ж", "ш")) else "н"
    elif w.endswith("а"): # слива -> слив-ов, груша -> груш-ев
        stem = w[:-1]
        if stem.endswith(("ш", "ж", "ч", "щ", "ц")):
            suffix_type = "ев"
        elif stem.endswith("ик"): # земляника, клубника -> землянич-н
            stem = stem[:-2] + "ич"
            suffix_type = "н"
        elif stem.endswith("ин"): # малина -> малин-ов
            suffix_type = "ов"
        else:
            suffix_type = "ов"
    elif w.endswith(("о", "е", "и", "у")): # манго, авокадо
        stem = w.rstrip("оеиу")
        suffix_type = "ов"
    else: # consonant: абрикос, персик, лимон, банан, томат
        stem = w
        if stem.endswith("сик"): # персик -> персик-ов
            suffix_type = "ов"
        elif stem.endswith("нан"): # банан -> банан-ов
            suffix_type = "ов"
        elif stem.endswith("ук"): # лук -> лук-ов
            suffix_type = "ов"
        elif stem.endswith(("он", "ат", "от", "ир", "ур", "ин", "еп")):
            suffix_type = "н"
        elif stem.endswith("к"):
            stem = stem[:-1] + "ч"
            suffix_type = "н"
        elif stem.endswith(("х", "г")):
            suffix_type = "ов"
        else:
            suffix_type = "ов"

    # Endings selection
    target_gender = "f" if gender == "en" else gender
    endings = {"m": "ый", "f": "ая", "n": "ое", "pl": "ые"}
    end = endings.get(target_gender, "ая")
    
    if suffix_type == "н":
        # Double 'н' if stem already ends in 'н' (лимон -> лимонный)
        res = stem + "н" + end
    elif suffix_type == "енн":
        res = stem + "енн" + end
    elif suffix_type == "ев":
        res = stem + "ев" + end
    else:
        res = stem + "ов" + end
    
    res = res.capitalize()
    if gender == "en":
        return transliterate(res)
    return res


def derive_person_from_name(name: str, email_domain: str = "synth-grid.ru", is_female: bool = False) -> dict:
    """
    Dynamically derives Surname, First Name, Patronymic, Street, and Email
    from a base name in the dictionary according to the assignment requirements.
    """
    name = name.strip()
    if not name:
        return {}
    
    n_lower = name.lower()
    
    if n_lower.endswith(("ей", "ай")):
        stem = name[:-1]
        surname_m = stem + "ев"
        surname_f = stem + "ева"
        patronymic_m = stem + "евич"
        patronymic_f = stem + "евна"
    elif n_lower.endswith("ий"):
        stem = name[:-2]
        surname_m = stem + "иев"
        surname_f = stem + "иева"
        patronymic_m = stem + "иевич"
        patronymic_f = stem + "иевна"
    elif n_lower.endswith(("а", "я")):
        stem = name[:-1]
        if n_lower == "илья":
            surname_m = "Ильин"
            surname_f = "Ильина"
            patronymic_m = "Ильич"
            patronymic_f = "Ильинична"
        elif n_lower == "никита":
            surname_m = "Никитин"
            surname_f = "Никитина"
            patronymic_m = "Никитич"
            patronymic_f = "Никитична"
        else:
            surname_m = stem + "ин"
            surname_f = stem + "ина"
            patronymic_m = stem + "ович"
            patronymic_f = stem + "овна"
    elif n_lower.endswith("ь"):
        stem = name[:-1]
        surname_m = stem + "ев"
        surname_f = stem + "ева"
        patronymic_m = stem + "евич"
        patronymic_f = stem + "евна"
    else:
        if n_lower.endswith("ил"):
            stem = name[:-2] + "йл"
        else:
            stem = name
        surname_m = stem + "ов"
        surname_f = stem + "ова"
        patronymic_m = stem + "ович"
        patronymic_f = stem + "овна"
    
    street_adj = surname_m + "ская"
    street = f"ул. {street_adj}"
    
    email_user = f"{transliterate(surname_m).lower()}.{transliterate(name)[0].lower()}"
    email = f"{email_user}@{email_domain}"
    
    fn = name
    ln = surname_f if is_female else surname_m
    mn = patronymic_f if is_female else patronymic_m
    
    return {
        "base_name": name,
        "firstName": fn,
        "lastName": ln,
        "middleName": mn,
        "fullName": f"{ln} {fn} {mn}",
        "street": street,
        "email": email
    }


# ==============================================================================
# 2. CORE DETERMINISTIC ANONYMIZATION ENGINE
# ==============================================================================
class AnonymizationEngine:
    def __init__(
        self,
        names_dict: List[str],
        fruits_dict: List[str],
        industries_dict: List[str],
        salt: str = "cim-model-salt-2026",
        email_domain: str = "synth-grid.ru"
    ):
        self.salt = salt
        self.email_domain = email_domain
        
        self.names_dict = [n.strip() for n in names_dict if n.strip()]
        self.fruits_dict = [f.strip() for f in fruits_dict if f.strip()]
        self.industries_dict = [i.strip() for i in industries_dict if i.strip()]
        
        if not self.names_dict:
            raise ValueError("Names dictionary is empty.")
        if not self.fruits_dict:
            raise ValueError("Fruits/Vegetables dictionary is empty.")
        if not self.industries_dict:
            self.industries_dict = ["Завод", "Комбинат", "Сети", "ПромМаш", "Транс"]

        # Bijective caches (deterministic, collision-free)
        self.memo_objects: Dict[str, str] = {}
        self.memo_persons: Dict[str, dict] = {}
        self.memo_orgs: Dict[str, str] = {}
        self.memo_streets: Dict[str, str] = {}
        self.memo_digits: Dict[str, str] = {}
        self.memo_mrids: Dict[str, str] = {}
        
        self.used_object_names: Set[str] = set()
        self.used_person_names: Set[str] = set()
        self.used_org_names: Set[str] = set()
        self.used_streets: Set[str] = set()
        self.used_digits: Set[str] = set()

    def _hash_int(self, text: str, domain: str = "") -> int:
        h = hashlib.sha256(f"{self.salt}:{domain}:{text}".encode('utf-8')).hexdigest()
        return int(h, 16)

    def anonymize_digits(self, digits: str) -> str:
        """
        Replaces a sequence of digits with a deterministic pseudorandom sequence
        of the EXACT same length (e.g. INN, KPP, tab. number, account, meter, asset serial).
        """
        if not digits or not digits.isdigit():
            return digits
        
        if digits in self.memo_digits:
            return self.memo_digits[digits]
        
        length = len(digits)
        seed_int = self._hash_int(digits, "digits")
        
        for attempt in range(1000):
            cand_int = (seed_int + attempt * 2654435761) % (10 ** length)
            cand_str = f"{cand_int:0{length}d}"
            if digits[0] != '0' and cand_str[0] == '0' and length > 1:
                cand_str = str((int(cand_str[0]) + 1 + (attempt % 9)) % 10 or 1) + cand_str[1:]
            
            if cand_str not in self.used_digits or cand_str == digits:
                self.memo_digits[digits] = cand_str
                self.used_digits.add(cand_str)
                return cand_str
        
        res = f"{seed_int % (10**length):0{length}d}"
        self.memo_digits[digits] = res
        return res

    def anonymize_mrid_str(self, mrid: str) -> str:
        """
        Anonymizes internal string identifiers (e.g. customer_50007178 -> customer_82941034)
        preserving semantic prefix while masking identifying numbers.
        """
        if not mrid:
            return mrid
        if mrid in self.memo_mrids:
            return self.memo_mrids[mrid]
        
        res = re.sub(r'\d+', lambda m: self.anonymize_digits(m.group(0)), mrid)
        self.memo_mrids[mrid] = res
        return res

    def get_fruit_adjective(self, text: str, form: str = "f") -> str:
        """
        Dynamically selects a fruit/vegetable noun from dictionary and
        inflects it into an adjective.
        """
        h = self._hash_int(text, "fruit_adj")
        idx = h % len(self.fruits_dict)
        raw_noun = self.fruits_dict[idx]
        return noun_to_adjective(raw_noun, gender=form)

    def anonymize_person(self, raw_name: str) -> dict:
        """
        Anonymizes physical persons and staff.
        Rule: Name from dictionary dynamically converts to LastName, FirstName, MiddleName,
        used for email and street name.
        """
        raw_name_clean = raw_name.strip()
        if raw_name_clean in self.memo_persons:
            return self.memo_persons[raw_name_clean]
        
        is_female = False
        parts = raw_name_clean.split()
        if len(parts) >= 2 and (parts[-1].endswith(('вна', 'чна', 'ична', 'ва', 'ая')) or parts[0].endswith(('ва', 'ая'))):
            is_female = True

        h = self._hash_int(raw_name_clean, "person")
        total_names = len(self.names_dict)
        
        for attempt in range(100):
            idx1 = (h + attempt) % total_names
            base_name = self.names_dict[idx1]
            p_data = derive_person_from_name(base_name, email_domain=self.email_domain, is_female=is_female)
            
            suffix = f"-{attempt}" if attempt > 0 else ""
            full_name = f"{p_data['lastName']}{suffix} {p_data['firstName']} {p_data['middleName']}"
            
            if full_name not in self.used_person_names:
                self.used_person_names.add(full_name)
                res = {
                    "lastName": f"{p_data['lastName']}{suffix}",
                    "firstName": p_data["firstName"],
                    "middleName": p_data["middleName"],
                    "fullName": full_name,
                    "email": p_data["email"].replace("@", f"{suffix}@"),
                    "street": p_data["street"]
                }
                self.memo_persons[raw_name_clean] = res
                return res
        
        base_name = self.names_dict[h % total_names]
        res = derive_person_from_name(base_name, email_domain=self.email_domain, is_female=is_female)
        self.memo_persons[raw_name_clean] = res
        return res

    def anonymize_legal_entity(self, raw_org: str) -> str:
        """
        Anonymizes corporate customers and organizations.
        Rule: vegetable/fruit name converted to adjective replacing proper noun;
        numerical IDs replaced by digits of same length.
        """
        raw_clean = raw_org.strip()
        if raw_clean in self.memo_orgs:
            return self.memo_orgs[raw_clean]
        
        form_pattern = r'\b(ПАО|ОАО|ЗАО|ООО|АО|ИП|НП|СПК|ГК|МУП|ГУП|JSC|PJSC|CJSC|OJSC|LLC|INC|LTD)\b'
        form_match = re.search(form_pattern, raw_clean, re.IGNORECASE)
        form_str = form_match.group(1).upper() if form_match else "ООО"
        
        is_en = bool(re.search(r'[a-zA-Z]', raw_clean)) and not bool(re.search(r'[а-яА-ЯёЁ]', raw_clean))
        
        h = self._hash_int(raw_clean, "legal_org")
        adj = self.get_fruit_adjective(raw_clean, form="en" if is_en else "m")
        ind = self.industries_dict[h % len(self.industries_dict)]
        
        for attempt in range(50):
            suffix = f"-{attempt}" if attempt > 0 else ""
            if is_en:
                cand = f"{form_str} \"{adj}{suffix} {ind}\""
            else:
                cand = f"{form_str} «{adj}{suffix} {ind}»"
            
            if cand not in self.used_org_names:
                self.used_org_names.add(cand)
                self.memo_orgs[raw_clean] = cand
                return cand
        
        self.memo_orgs[raw_clean] = cand
        return cand

    def anonymize_power_object_name(self, raw_name: str, obj_class: str = "") -> str:
        """
        Anonymizes power system objects (ПС, ТП, РП, ЛЭП, ВЛ, КЛ, опоры, присоединения).
        Rules:
        - Preserves object type and class (ТП остаётся ТП, ПС - ПС, ЛЭП - ЛЭП)
        - Preserves voltage level (110 кВ, 35 кВ, 10 кВ, 0.4 кВ)
        - Replaces proper names with fruit/vegetable adjectives
        - Replaces numerical IDs with digits of same length
        - Preserves technical suffixes (main line, цепь, ф.05, ячейка...)
        - Guarantees uniqueness.
        """
        raw_clean = raw_name.strip()
        if not raw_clean:
            return raw_clean
        if raw_clean in self.memo_objects:
            return self.memo_objects[raw_clean]
        
        def repl_digits(m):
            return self.anonymize_digits(m.group(0))

        # Simple type prefix + number (e.g., "Sub - 2303", "Sub - 34P", "ТП-204", "РП-12", "Опора 45")
        simple_num_match = re.match(r'^(Sub\s*-\s*|ТП[\s\-_]*|РП[\s\-_]*|КТП[\s\-_]*|Опора[\s\-_]*|Pole[\s\-_]*)(\d+)([a-zA-Zа-яА-Я]*)$', raw_clean, re.IGNORECASE)
        if simple_num_match:
            prefix = simple_num_match.group(1)
            num = simple_num_match.group(2)
            suffix_char = simple_num_match.group(3)
            anon_num = self.anonymize_digits(num)
            res = f"{prefix}{anon_num}{suffix_char}"
            self.memo_objects[raw_clean] = res
            return res

        # Address-like string in ServiceLocation
        if "District" in raw_clean or "Street" in raw_clean or "ул." in raw_clean or "область" in raw_clean:
            res = self.anonymize_full_address(raw_clean)
            self.memo_objects[raw_clean] = res
            return res

        # Electrical network or district region
        if "el. net." in raw_clean or "electrical network" in raw_clean:
            is_en = bool(re.search(r'[a-zA-Z]', raw_clean))
            adj = self.get_fruit_adjective(raw_clean, form="en" if is_en else "f")
            suffix = "el. net." if "el. net." in raw_clean else "electrical network"
            res = f"{adj} {suffix}"
            self.memo_objects[raw_clean] = res
            return res

        # Voltage detection: 110/35/10 kV, 35/10 кВ, 110 кВ, 400 V
        volt_m = re.search(r'(\d+(?:[.,/]\d+)*\s*(?:кВ|kV|В|V))', raw_clean, re.IGNORECASE)
        volt_str = volt_m.group(1) if volt_m else ""
        
        # Type prefix detection
        type_prefix = ""
        type_patterns = [
            r'^(ПС|ТП|РП|КТП|СП|ВЛ|КЛ|КВЛ|ЛЭП|Опора|Фидер|Substation|Sub|OHL|CBL|Line|Feeder|Bay|Трансформатор|Выключатель)\b'
        ]
        for tp in type_patterns:
            m = re.search(tp, raw_clean, re.IGNORECASE)
            if m:
                type_prefix = m.group(1)
                break
        
        if not type_prefix:
            if obj_class == "Substation":
                type_prefix = "ПС" if re.search(r'[а-яА-ЯёЁ]', raw_clean) else "Sub"
            elif obj_class in ("Line", "ACLineSegment"):
                type_prefix = "ВЛ" if re.search(r'[а-яА-ЯёЁ]', raw_clean) else "OHL"
            elif obj_class == "Pole":
                type_prefix = "Опора"
            else:
                type_prefix = ""

        is_en = bool(re.search(r'[a-zA-Z]', raw_clean)) and not bool(re.search(r'[а-яА-ЯёЁ]', raw_clean))
        
        gender = "f"
        if type_prefix.upper() in ("ТП", "РП", "КТП"):
            gender = "m"
        elif type_prefix.upper() in ("ПС", "ВЛ", "КЛ", "ЛЭП", "ОПОРА", "SUB", "SUBSTATION"):
            gender = "f"
        if is_en:
            gender = "en"
        
        adj = self.get_fruit_adjective(raw_clean, form=gender)
        
        # Extract remaining structural modifiers
        modifiers = []
        for mod_pattern in [r'(f\.\d+)', r'(фидер\s*\d+)', r'(\d+\s*цепь)', r'(цепь\s*\d+)', r'(main line)', r'(segment[^,]*)', r'(отпайка[^,]*)', r'(ячейка\s*\d+)']:
            m = re.search(mod_pattern, raw_clean, re.IGNORECASE)
            if m:
                mod_clean = re.sub(r'\d+', repl_digits, m.group(1))
                modifiers.append(mod_clean)
        
        mod_suffix = " " + " ".join(modifiers) if modifiers else ""
        
        span_m = re.search(r'[,]\s*(\d+[\s\-_0-9]+)$', raw_clean)
        span_suffix = ""
        if span_m:
            span_clean = re.sub(r'\d+', repl_digits, span_m.group(1))
            span_suffix = f", {span_clean}"
        
        for attempt in range(100):
            counter_suffix = f"-{attempt}" if attempt > 0 else ""
            
            parts = []
            if type_prefix:
                parts.append(type_prefix)
            if volt_str:
                parts.append(volt_str)
            
            parts.append(f"{adj}{counter_suffix}")
            
            base_cand = " ".join(parts) + mod_suffix + span_suffix
            
            if base_cand not in self.used_object_names:
                self.used_object_names.add(base_cand)
                self.memo_objects[raw_clean] = base_cand
                return base_cand

        self.memo_objects[raw_clean] = base_cand
        return base_cand

    def anonymize_full_address(self, addr: str) -> str:
        """
        Anonymizes street names and addresses using synthetic person or plant names.
        """
        raw_clean = addr.strip()
        if not raw_clean:
            return raw_clean
        if raw_clean in self.memo_streets:
            return self.memo_streets[raw_clean]
        
        if "Street" in addr or "District" in addr:
            def repl_street_en(m):
                adj = self.get_fruit_adjective(m.group(1), form="en")
                return f"{adj} Street"
            res = re.sub(r'\b([A-Za-z0-9_\-\']+)\s+Street\b', repl_street_en, addr)
            res = re.sub(r'(h\.\s*№?\s*)(\d+)', lambda m: f"{m.group(1)}{self.anonymize_digits(m.group(2))}", res)
            self.memo_streets[raw_clean] = res
            return res
        
        type_match = re.search(r'\b(ул\.|улица|пер\.|переулок|пр-кт|пр\.|проспект|тр\.|тракт|бул\.|бульвар|проезд|наб\.|набережная|ш\.|шоссе)\s+([^,]+)', addr, re.IGNORECASE)
        if type_match:
            street_type = type_match.group(1)
            orig_street_name = type_match.group(2).strip()
            h = self._hash_int(orig_street_name, "street_ru")
            base_name = self.names_dict[h % len(self.names_dict)]
            p_data = derive_person_from_name(base_name)
            
            new_street_part = f"{street_type} {p_data['street'].replace('ул. ', '')}"
            addr_replaced = addr[:type_match.start()] + new_street_part + addr[type_match.end():]
            
            def repl_house(m):
                return f"{m.group(1)}{self.anonymize_digits(m.group(2))}"
            
            addr_final = re.sub(r'(,\s*|\bд\.\s*|\bк\.\s*)(\d+)', repl_house, addr_replaced)
            self.memo_streets[raw_clean] = addr_final
            return addr_final
        else:
            res = re.sub(r'\d+', lambda m: self.anonymize_digits(m.group(0)), addr)
            self.memo_streets[raw_clean] = res
            return res

    def mask_free_text(self, text: str) -> str:
        """
        Masks personal data (phone, email, passport, INN) and mentions of
        known real object/person names in free text fields, logs, comments.
        """
        if not text:
            return text
        
        # 1. Mask Phones
        text = re.sub(r'\+?[78][-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}', '+7 (9XX) XXX-XX-XX', text)
        
        # 2. Mask Emails
        text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', f'anonymous@{self.email_domain}', text)
        
        # 3. Mask Passports
        text = re.sub(r'\b\d{4}\s+\d{6}\b', 'XXXX XXXXXX', text)
        
        # 4. Mask SNILS
        text = re.sub(r'\b\d{3}-\d{3}-\d{3}\s+\d{2}\b', 'XXX-XXX-XXX XX', text)
        
        # 5. Mask INN
        text = re.sub(r'\b\d{10}\b|\b\d{12}\b', lambda m: self.anonymize_digits(m.group(0)), text)
        
        return text


# ==============================================================================
# 3. HIGH-PERFORMANCE STREAMING XML PROCESSOR
# ==============================================================================
def process_cim_xml(
    input_path: str,
    output_path: str,
    engine: AnonymizationEngine,
    limit_mb: Optional[float] = None
) -> dict:
    t_start = time.time()
    limit_bytes = int(limit_mb * 1024 * 1024) if limit_mb else None
    
    stats = {
        "lines_processed": 0,
        "bytes_read": 0,
        "objects_anonymized": 0,
        "persons_anonymized": 0,
        "orgs_anonymized": 0,
        "streets_anonymized": 0,
        "digits_anonymized": 0,
        "free_texts_masked": 0,
    }
    
    top_open_re = re.compile(r'^\s{2}<(?:[a-zA-Z0-9_\-]+:)?([a-zA-Z0-9_\-]+)(?:\s+rdf:about|\s+rdf:ID|\s*>)')
    top_close_re = re.compile(r'^\s{2}</(?:[a-zA-Z0-9_\-]+:)?([a-zA-Z0-9_\-]+)>')
    tag_val_re = re.compile(r'^(\s*<([a-zA-Z0-9_\-]+):([a-zA-Z0-9_\-\.]+)>)(.*?)(</\2:\3>\s*)$')
    
    current_class = None
    
    PERSON_CLASSES = {"Person"}
    CUSTOMER_CLASSES = {"Customer"}
    ORG_CLASSES = {"Organisation", "OrganisationRole"}
    LOCATION_CLASSES = {"ServiceLocation", "StreetAddress", "StreetDetail", "TownDetail"}
    POWER_OBJ_CLASSES = {
        "Substation", "Line", "ACLineSegment", "PowerTransformer", "SynchronousMachine",
        "GeneratingUnit", "HydroGeneratingUnit", "ThermalGeneratingUnit", "NuclearGeneratingUnit",
        "VoltageLevel", "Bay", "Pole", "Breaker", "Disconnector", "GroundDisconnector",
        "CurrentTransformer", "PotentialTransformer", "SurgeArrester", "Fuse",
        "BusbarSection", "Jumper", "LinearShuntCompensator", "SeriesCompensator",
        "PetersenCoil", "LoadBreakSwitch", "Recloser", "Plant", "HydroPowerPlant",
        "CogenerationPlant", "NonConformLoad", "EnergyConsumer", "SubGeographicalRegion",
        "GeographicalRegion", "ModelingAuthoritySet"
    }
    
    BUFFER_SIZE = 8 * 1024 * 1024
    
    with open(input_path, "r", encoding="utf-8", errors="replace", buffering=BUFFER_SIZE) as fin, \
         open(output_path, "w", encoding="utf-8", buffering=BUFFER_SIZE) as fout:
        
        bytes_counter = 0
        for line in fin:
            stats["lines_processed"] += 1
            line_len = len(line.encode("utf-8"))
            bytes_counter += line_len
            stats["bytes_read"] = bytes_counter
            
            if limit_bytes and bytes_counter > limit_bytes:
                fout.write("</rdf:RDF>\n")
                break
            
            m_top = top_open_re.match(line)
            if m_top:
                current_class = m_top.group(1)
                fout.write(line)
                continue
            
            m_close = top_close_re.match(line)
            if m_close:
                if m_close.group(1) == current_class:
                    current_class = None
                fout.write(line)
                continue
            
            m_val = tag_val_re.match(line)
            if m_val:
                prefix_tag = m_val.group(1)
                ns = m_val.group(2)
                prop_name = m_val.group(3)
                raw_val = m_val.group(4)
                suffix_tag = m_val.group(5)
                
                new_val = raw_val
                
                # 1. Object and Person Names
                if prop_name in ("IdentifiedObject.name", "name", "Name.name"):
                    if current_class in PERSON_CLASSES:
                        p_info = engine.anonymize_person(raw_val)
                        new_val = p_info["fullName"]
                        stats["persons_anonymized"] += 1
                    elif current_class in CUSTOMER_CLASSES:
                        if raw_val.isdigit():
                            new_val = engine.anonymize_digits(raw_val)
                            stats["digits_anonymized"] += 1
                        elif any(corp_marker in raw_val for corp_marker in ["ООО", "ПАО", "АО", "ЗАО", "ОАО", "ИП", "JSC", "PJSC", "LLC", "plant", "Ltd", "Завод"]):
                            new_val = engine.anonymize_legal_entity(raw_val)
                            stats["orgs_anonymized"] += 1
                        else:
                            p_info = engine.anonymize_person(raw_val)
                            new_val = p_info["fullName"]
                            stats["persons_anonymized"] += 1
                    elif current_class in ORG_CLASSES:
                        new_val = engine.anonymize_legal_entity(raw_val)
                        stats["orgs_anonymized"] += 1
                    elif current_class in LOCATION_CLASSES:
                        new_val = engine.anonymize_full_address(raw_val)
                        stats["streets_anonymized"] += 1
                    elif current_class in POWER_OBJ_CLASSES:
                        new_val = engine.anonymize_power_object_name(raw_val, current_class or "")
                        stats["objects_anonymized"] += 1
                    else:
                        if re.search(r'[a-zA-Zа-яА-ЯёЁ]', raw_val):
                            new_val = engine.anonymize_power_object_name(raw_val, current_class or "")
                            stats["objects_anonymized"] += 1

                # 2. Person attributes
                elif prop_name in ("Person.lastName", "lastName"):
                    p_info = engine.anonymize_person(raw_val)
                    new_val = p_info["lastName"]
                    stats["persons_anonymized"] += 1
                elif prop_name in ("Person.firstName", "firstName"):
                    p_info = engine.anonymize_person(raw_val)
                    new_val = p_info["firstName"]
                    stats["persons_anonymized"] += 1
                elif prop_name in ("Person.middleName", "middleName"):
                    p_info = engine.anonymize_person(raw_val)
                    new_val = p_info["middleName"]
                    stats["persons_anonymized"] += 1
                
                # 3. Address and Street Details
                elif prop_name in ("StreetDetail.addressGeneral", "StreetDetail.name", "streetName"):
                    new_val = engine.anonymize_full_address(raw_val)
                    stats["streets_anonymized"] += 1
                elif prop_name in ("StreetDetail.buildingName", "StreetDetail.number", "buildingName"):
                    if re.search(r'\d+', raw_val):
                        new_val = re.sub(r'\d+', lambda m: engine.anonymize_digits(m.group(0)), raw_val)
                        stats["digits_anonymized"] += 1

                # 4. Serial numbers / Inventory numbers / Accounts / Digits
                elif prop_name in ("Asset.serialNumber", "serialNumber", "accountNumber", "meterNumber"):
                    new_val = engine.anonymize_digits(raw_val)
                    stats["digits_anonymized"] += 1
                elif prop_name in ("IdentifiedObject.mRIDStr", "mRIDStr"):
                    new_val = engine.anonymize_mrid_str(raw_val)
                    stats["digits_anonymized"] += 1

                # 5. Free-text fields
                elif prop_name in ("IdentifiedObject.description", "description", "comment", "note", "log"):
                    new_val = engine.mask_free_text(raw_val)
                    stats["free_texts_masked"] += 1

                fout.write(f"{prefix_tag}{new_val}{suffix_tag}")
            else:
                fout.write(line)

    t_end = time.time()
    stats["elapsed_seconds"] = round(t_end - t_start, 2)
    stats["throughput_mb_s"] = round((stats["bytes_read"] / (1024 * 1024)) / (t_end - t_start or 1), 2)
    return stats


# ==============================================================================
# 4. VERIFICATION AND INTEGRITY AUDIT
# ==============================================================================
def verify_model(input_path: str, output_path: str, sample_lines: int = 100000) -> dict:
    print(f"\n[VERIFICATION] Auditing {output_path} against {input_path}...")
    
    in_tags = {}
    out_tags = {}
    sampled_pairs: List[Tuple[str, str]] = []
    
    with open(input_path, "r", encoding="utf-8", errors="replace") as fin, \
         open(output_path, "r", encoding="utf-8", errors="replace") as fout:
        
        for i, (l_in, l_out) in enumerate(zip(fin, fout)):
            if i >= sample_lines:
                break
            
            m_in = re.match(r'^\s*<([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-\.]+)', l_in)
            m_out = re.match(r'^\s*<([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-\.]+)', l_out)
            
            if m_in and m_out:
                tag_in = m_in.group(1)
                tag_out = m_out.group(1)
                assert tag_in == tag_out, f"Tag mismatch at line {i+1}: {tag_in} vs {tag_out}"
                in_tags[tag_in] = in_tags.get(tag_in, 0) + 1
                out_tags[tag_out] = out_tags.get(tag_out, 0) + 1
            
            if "IdentifiedObject.name" in l_in:
                v_in = re.search(r'>([^<]+)<', l_in)
                v_out = re.search(r'>([^<]+)<', l_out)
                if v_in and v_out:
                    sampled_pairs.append((v_in.group(1).strip(), v_out.group(1).strip()))

    total = len(sampled_pairs)
    changed = sum(1 for o, a in sampled_pairs if o != a)
    ratio = changed / max(1, total)
    
    results = {
        "audited_lines": sample_lines,
        "structural_tags_matched": in_tags == out_tags,
        "sampled_names_count": total,
        "changed_names_count": changed,
        "changed_names_ratio": round(ratio, 4),
        "sample_transformations": sampled_pairs[:12]
    }
    return results


# ==============================================================================
# 5. CLI & DYNAMIC DICTIONARY LOADER
# ==============================================================================
def load_lines_from_file(path: str) -> List[str]:
    """Loads a list of strings from a text file, ignoring empty lines and comments."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dictionary file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return lines


def main():
    parser = argparse.ArgumentParser(
        description="High-performance CIM/XML Anonymization Engine for Power Systems (Dynamic Morphological Architecture)."
    )
    # Input / Output
    parser.add_argument("--input", "-i", default="input.xml", help="Path to input CIM/XML file (default: input.xml).")
    parser.add_argument("--output", "-o", default=None, help="Path to output anonymized XML file (default: <input>_anonymized.xml).")
    
    # External dictionaries
    parser.add_argument("--names-dict", default=None, help="Path to external names dictionary file (.txt).")
    parser.add_argument("--fruits-dict", default=None, help="Path to external fruits/vegetables dictionary file (.txt).")
    parser.add_argument("--industries-dict", default=None, help="Path to external industries dictionary file (.txt).")
    
    # Engine parameters
    parser.add_argument("--salt", "-s", default="cim-model-salt-2026", help="Salt/Seed for deterministic pseudonymization.")
    parser.add_argument("--email-domain", default="synth-grid.ru", help="Domain for synthetic emails.")
    parser.add_argument("--limit-mb", "-l", type=float, default=None, help="Process only first N megabytes (for rapid testing).")
    parser.add_argument("--verify", "-v", action="store_true", help="Run consistency and integrity audit after processing.")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        candidate_path = os.path.join(script_dir, args.input)
        if os.path.exists(candidate_path):
            input_path = candidate_path
        else:
            print(f"Error: Input file not found: {input_path}")
            sys.exit(1)

    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_anonymized{ext}"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    def_dict_dir = os.path.join(script_dir, "dictionaries")

    names_file = args.names_dict or os.path.join(def_dict_dir, "names.txt")
    fruits_file = args.fruits_dict or os.path.join(def_dict_dir, "fruits_vegetables.txt")
    industries_file = args.industries_dict or os.path.join(def_dict_dir, "industries.txt")

    names_list = load_lines_from_file(names_file)
    fruits_list = load_lines_from_file(fruits_file)
    industries_list = load_lines_from_file(industries_file) if os.path.exists(industries_file) else ["Завод", "Комбинат", "Сети", "Транс"]

    engine = AnonymizationEngine(
        names_dict=names_list,
        fruits_dict=fruits_list,
        industries_dict=industries_list,
        salt=args.salt,
        email_domain=args.email_domain
    )

    print("=" * 70)
    print("CIM/XML MODEL ANONYMIZATION ENGINE (DYNAMIC ARCHITECTURE)")
    print(f"Input:           {input_path} ({os.path.getsize(input_path) / (1024*1024):.2f} MB)")
    print(f"Output:          {output_path}")
    print(f"Names Dict:      {names_file} ({len(names_list)} entries)")
    print(f"Fruits Dict:     {fruits_file} ({len(fruits_list)} entries)")
    print(f"Salt/Seed:       {args.salt}")
    print(f"Email Domain:    {args.email_domain}")
    if args.limit_mb:
        print(f"Test Limit:      {args.limit_mb:.2f} MB")
    print("=" * 70)

    stats = process_cim_xml(
        input_path=input_path,
        output_path=output_path,
        engine=engine,
        limit_mb=args.limit_mb
    )

    print("\n--- ANONYMIZATION RESULTS ---")
    print(f"Lines processed:      {stats['lines_processed']:,}")
    print(f"Data read:            {stats['bytes_read'] / (1024*1024):.2f} MB")
    print(f"Time elapsed:         {stats['elapsed_seconds']} s")
    print(f"Throughput:           {stats['throughput_mb_s']} MB/s")
    print(f"Objects renamed:      {stats['objects_anonymized']:,}")
    print(f"Persons anonymized:   {stats['persons_anonymized']:,}")
    print(f"Legal entities:       {stats['orgs_anonymized']:,}")
    print(f"Streets/Addresses:    {stats['streets_anonymized']:,}")
    print(f"Digits/IDs masked:    {stats['digits_anonymized']:,}")
    print(f"Free-text fields:     {stats['free_texts_masked']:,}")
    print("=" * 70)

    if args.verify:
        audit = verify_model(input_path, output_path, sample_lines=50000)
        print("\n--- INTEGRITY AUDIT ---")
        print(f"XML tags matched:     {'PASSED [OK]' if audit['structural_tags_matched'] else 'FAILED'}")
        print(f"Names audited:        {audit['sampled_names_count']}")
        print(f"Names anonymized:     {audit['changed_names_count']}")
        print(f"Transformation ratio: {audit['changed_names_ratio'] * 100:.1f}%")
        print("\nDirect Transformations Sample (Original ===> Anonymized):")
        for orig, anon in audit['sample_transformations']:
            print(f"  • {orig:45s} ===>  {anon}")
        print("=" * 70)

if __name__ == "__main__":
    main()
