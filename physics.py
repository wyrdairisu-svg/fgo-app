import math

# ==========================================
# FGO Physics Constants & Matrices
# ==========================================

# Class Affinity Matrix (Attacker vs Defender)
# 2.0 = Advantage, 0.5 = Disadvantage, 1.0 = Neutral, 1.5 = Berserker/AlterEgo
CLASS_AFFINITY = {
    'saber': {'lancer': 2.0, 'archer': 0.5, 'berserker': 2.0, 'ruler': 0.5},
    'archer': {'saber': 2.0, 'lancer': 0.5, 'berserker': 2.0, 'ruler': 0.5},
    'lancer': {'archer': 2.0, 'saber': 0.5, 'berserker': 2.0, 'ruler': 0.5},
    'rider': {'caster': 2.0, 'assassin': 0.5, 'berserker': 2.0, 'ruler': 0.5, 'alterego': 0.5, 'pretender': 2.0},
    'caster': {'assassin': 2.0, 'rider': 0.5, 'berserker': 2.0, 'ruler': 0.5, 'alterego': 0.5, 'pretender': 2.0},
    'assassin': {'rider': 2.0, 'caster': 0.5, 'berserker': 2.0, 'ruler': 0.5, 'alterego': 0.5, 'pretender': 2.0},
    'berserker': {'shielder': 1.0, 'foreigner': 0.5, 'beast': 1.0}, # Bezerker is 1.5 vs ALMOST ALL (handled in function)
    'ruler': {'moon_cancer': 2.0, 'avenger': 0.5, 'berserker': 2.0},
    'avenger': {'ruler': 2.0, 'moon_cancer': 0.5, 'berserker': 2.0},
    'moon_cancer': {'avenger': 2.0, 'ruler': 0.5, 'berserker': 2.0},
    'alterego': {'rider': 1.5, 'caster': 1.5, 'assassin': 1.5, 'saber': 0.5, 'archer': 0.5, 'lancer': 0.5, 'foreigner': 2.0, 'berserker': 2.0, 'pretender': 0.5},
    'foreigner': {'foreigner': 2.0, 'berserker': 2.0, 'alterego': 0.5, 'pretender': 2.0},
    'pretender': {'saber': 1.5, 'archer': 1.5, 'lancer': 1.5, 'rider': 0.5, 'caster': 0.5, 'assassin': 0.5, 'alterego': 2.0, 'berserker': 2.0},
    'shielder': {},
    'beast': {} # Complex, usually depends on specific Beast II/III etc.
}

# Generic fallback for Berserker attacker vs others = 1.5
# Generic fallback for Others vs Berserker = 2.0

# Attribute Affinity (Attacker vs Defender)
# Sky (Ten) > Earth (Chi) > Man (Jin) > Sky (Ten) [1.1x]
# Reverse is [0.9x]
# Star/Beast usually 1.0
ATTRIBUTE_AFFINITY = {
    'sky': {'earth': 1.1, 'man': 0.9},
    'earth': {'man': 1.1, 'sky': 0.9},
    'man': {'sky': 1.1, 'earth': 0.9},
    'star': {},
    'beast': {}
}

# Class Damage Multipliers
CLASS_MULTIPLIER = {
    'saber': 1.0, 'archer': 0.95, 'lancer': 1.05,
    'rider': 1.0, 'caster': 0.9, 'assassin': 0.9,
    'berserker': 1.1, 'ruler': 1.1, 'avenger': 1.1,
    'moon_cancer': 1.0, 'alterego': 1.0, 'foreigner': 1.0,
    'pretender': 1.0, 'shielder': 1.0
}

# ==========================================
# Core Functions
# ==========================================

def get_class_modifier(attacker_class, defender_class):
    """
    Get strict class affinity modifier.
    """
    atk = attacker_class.lower()
    dfd = defender_class.lower()
    
    # 1. Check Berserker Special Cases
    if atk == 'berserker':
        if dfd == 'foreigner': return 0.5
        if dfd == 'shielder': return 1.0
        # Vs Beast is complicated but usually 1.5 or 1.0
        return 1.5
    
    if dfd == 'berserker':
        # Foreigner takes neutral? No, Berserker deals 1.5 to Foreigner, Foreigner deals 2.0 to Berserker.
        # Wait, Foreigner takes 0.5 from Berserker. (Handled above)
        # Everyone else deals 2.0 to Berserker (except Shielder)
        if atk == 'shielder': return 1.0
        return 2.0

    # 2. Lookup Matrix
    if atk in CLASS_AFFINITY:
        if dfd in CLASS_AFFINITY[atk]:
            return CLASS_AFFINITY[atk][dfd]
            
    return 1.0

def get_attribute_modifier(attacker_attr, defender_attr):
    """
    Get Attirbute (Ten/Chi/Jin) modifier.
    """
    atk = str(attacker_attr).lower()
    dfd = str(defender_attr).lower()
    
    if atk in ATTRIBUTE_AFFINITY:
        return ATTRIBUTE_AFFINITY[atk].get(dfd, 1.0)
    return 1.0

def calculate_damage_min(atk_stat, np_multiplier, 
                         card_mod=0.0, atk_mod=0.0, def_down_mod=0.0, 
                         power_mod=0.0, np_dmg_mod=0.0, super_effective_mod=0.0,
                         class_mult=1.0, class_affinity=2.0, attr_affinity=1.0,
                         is_np=True):
    """
    Calculate Minimum Damage (RNG 0.9).
    Theory B: Determinism over Expectation.
    
    Formula:
    DMG = (ATK * NP_Mult * (CardMod) * ClassMult * ClassAffinity * AttrAffinity * 0.23 * RNG(0.9)) 
          * (1 + AtkMod + DefDown) 
          * (1 + NP_Dmg_Mod + PowerMod) 
          * (1 + SuperEffectiveMod) 
          + FlatDamage
    """
    
    # Base Factors
    # NP Multiplier is in %, e.g. 450% -> 4.5
    # Card Mod: Arts/Quick/Buster performance + Card type constant (A=1.0, B=1.5, Q=0.8 for NP)
    # Note: calculate_damage_min expects pre-summed modifiers (e.g. card_mod = 1.0 (base) + 0.5 (buff) = 1.5)
    
    # Standard FGO constant
    base = atk_stat * np_multiplier * 0.23
    
    # Multipliers
    factors = (
        class_mult * 
        class_affinity * 
        attr_affinity * 
        0.9 # RNG MINIMUM (Theory B)
    )
    
    damage_pre_buffs = base * factors * card_mod
    
    # Buff Buckets (Theory A)
    bucket_atk = max(0.0, 1.0 + atk_mod + def_down_mod) # Assumes mods are 0.2 for 20%
    bucket_power = max(0.0, 1.0 + np_dmg_mod + power_mod)
    bucket_special = max(0.0, 1.0 + super_effective_mod)
    
    total_damage = damage_pre_buffs * bucket_atk * bucket_power * bucket_special
    
    return int(total_damage)

def calculate_refund(np_gain, hits, 
                     card_mod=0.0, np_gain_mod=0.0, 
                     overkill_hits=0, enemy_server_mod=1.0):
    """
    Calculate NP Refund per enemy.
    
    Formula:
    Refund = BaseNPGain * Hits * EnemyMod(Server) * (1 + CardMod) * (1 + NPGainMod) * OverkillMod
    """
    
    # Base calculation per hit
    # In reality, need to sum per hit because overkill changes per hit.
    # Provided 'hits' is total hits.
    # 'overkill_hits' is how many of those were overkill.
    
    # Constants
    # Arts Base = 3.0? No, Card Type Multiplier. 
    # This function expects 'np_gain' to be the raw "N/A" value * Card Type Multiplier
    # (e.g. 0.54 * 3.0 for Arts NP).
    # Please provide PRE-MULTIPLIED np_gain aka "Scaurce N/A * CardConstant".
    
    total_refund = 0.0
    
    # Modifiers
    buffs = max(0.0, (1.0 + card_mod) * (1.0 + np_gain_mod))
    
    # Normal Hits
    normal_hits = hits - overkill_hits
    if normal_hits > 0:
        total_refund += np_gain * normal_hits * enemy_server_mod * buffs
        
    # Overkill Hits (1.5x)
    if overkill_hits > 0:
        total_refund += np_gain * overkill_hits * enemy_server_mod * buffs * 1.5
        
    return math.floor(total_refund * 100) / 100 # Return e.g. 15.45

# Mock Data for testing
class Servant:
    def __init__(self, name, atk, np_gain_atk, hits_np, card_np):
        self.name = name
        self.atk = atk
        self.np_gain_atk = np_gain_atk
        self.hits_np = hits_np
        self.card_np = card_np # 'Arts', 'Buster', 'Quick'

class Enemy:
    def __init__(self, class_name, server_mod=1.0):
        self.class_name = class_name
        self.server_mod = server_mod

# Server Mod Table (Partial)
SERVER_MODS = {
    'rider': 1.1, 'caster': 1.2, 'assassin': 0.9, 'berserker': 0.8, 'moon_cancer': 1.2
}
