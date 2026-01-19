SCALE_MODES = {
    # Common diatonic (7-note)
    "ionian_major":               [2, 2, 1, 2, 2, 2, 1],  # same as "major"
    "dorian":                     [2, 1, 2, 2, 2, 1, 2],
    "phrygian":                   [1, 2, 2, 2, 1, 2, 2],
    "lydian":                     [2, 2, 2, 1, 2, 2, 1],
    "mixolydian":                 [2, 2, 1, 2, 2, 1, 2],
    "aeolian_natural_minor":      [2, 1, 2, 2, 1, 2, 2],  # same as "minor"
    "locrian":                    [1, 2, 2, 1, 2, 2, 2],

    # Harmonic / melodic minor families (7-note)
    "harmonic_minor":             [2, 1, 2, 2, 1, 3, 1],
    "melodic_minor":              [2, 1, 2, 2, 2, 2, 1],  # jazz melodic minor (asc)

    # Modes of harmonic minor (exotic but common in theory)
    "harmonic_minor_mode2_locrian_nat6": [1, 2, 1, 2, 2, 1, 3],
    "harmonic_minor_mode3_ionian_aug":   [2, 1, 2, 2, 1, 3, 1],  # same pitch steps as harmonic_minor rotation varies by root
    "harmonic_minor_mode4_dorian_4":     [2, 2, 1, 2, 1, 3, 1],
    "harmonic_minor_mode5_phrygian_dom": [1, 3, 1, 2, 1, 2, 2],
    "harmonic_minor_mode6_lydian_2":     [3, 1, 2, 1, 2, 2, 1],
    "harmonic_minor_mode7_superlocrian_bb7": [1, 2, 1, 2, 2, 1, 3],

    # Modes of melodic minor (very used in jazz)
    "dorian_b2":                  [1, 2, 2, 2, 2, 1, 2],
    "lydian_aug":                 [2, 2, 2, 2, 1, 2, 1],
    "lydian_dom":                 [2, 2, 2, 1, 2, 1, 2],  # aka acoustic scale
    "mixolydian_b6":              [2, 2, 1, 2, 1, 2, 2],
    "locrian_nat2":               [2, 1, 2, 1, 2, 2, 2],
    "altered_superlocrian":       [1, 2, 1, 2, 2, 2, 2],  # altered scale

    # Pentatonics (5-note)
    "pentatonic_major":           [2, 2, 3, 2, 3],
    "pentatonic_minor":           [3, 2, 2, 3, 2],
    "egyptian_pentatonic":        [2, 3, 2, 3, 2],
    "hirajoshi":                  [2, 1, 4, 1, 4],
    "iwato":                      [1, 4, 1, 4, 2],
    "kumoi":                      [2, 1, 4, 2, 3],
    "insen":                      [1, 4, 2, 3, 2],
    "yo":                         [2, 3, 2, 2, 3],  # Japanese "Yo" pentatonic

    # Blues / hexatonics (6-note)
    "blues":                      [3, 2, 1, 1, 3, 2],
    "whole_tone":                 [2, 2, 2, 2, 2, 2],
    "augmented_hexatonic":        [3, 1, 3, 1, 3, 1],  # symmetric (aka augmented scale)
    "prometheus":                 [2, 2, 2, 3, 1, 2],  # Prometheus scale
    "tritone_scale":              [1, 2, 1, 2, 1, 2, 3],  # less standard naming, but useful pattern

    # Octatonics (8-note, symmetric)
    "diminished_hw":              [1, 2, 1, 2, 1, 2, 1, 2],  # half-whole
    "diminished_wh":              [2, 1, 2, 1, 2, 1, 2, 1],  # whole-half

    # Common exotic heptatonics (7-note)
    "hungarian_minor":            [2, 1, 3, 1, 1, 3, 1],
    "double_harmonic_major":      [1, 3, 1, 2, 1, 3, 1],  # Byzantine
    "neapolitan_minor":           [1, 2, 2, 2, 1, 3, 1],
    "neapolitan_major":           [1, 2, 2, 2, 2, 2, 1],
    "enigmatic":                  [1, 3, 2, 2, 2, 1, 1],
    "persian":                    [1, 3, 1, 1, 2, 3, 1],
    "romanian_minor":             [2, 1, 3, 1, 2, 1, 2],
    "ukrainian_dorian":           [2, 1, 3, 1, 2, 1, 2],  # often same as romanian_minor labeling varies
    "spanish_gypsy":              [1, 3, 1, 2, 1, 2, 2],  # Phrygian dominant (alt name)

    # Chromatic / special
    "chromatic":                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
}

