import Foundation

// MARK: - Top Level Servant Detail
struct ServantDetail: Codable, Identifiable {
    let id: Int
    let collectionNo: Int
    let name: String
    let className: String // "className" in JSON
    let rarity: Int
    let cost: Int
    let hpMax: Int
    let atkMax: Int
    let attribute: String
    
    // Cards & Hits
    let cards: [String] // ["arts", "arts", "quick", ...]
    let hitsDistribution: [String: [Int]]?
    
    // Hidden Stats
    let starAbsorb: Int?
    let starGen: Int?
    // NP Charge Rate often found in "noblePhantasms" first entry or specific property
    // We will extract from first NP if available for general purpose
    
    // Complex Data
    let traits: [Trait]
    let skills: [Skill]
    let noblePhantasms: [NoblePhantasm]
    
    // Computed formatting
    var faceUrl: URL? {
        // Construct standard URL or use one from JSON if "face" exists
        // Atlas API returns "face" usually
        return nil 
    }
}

// MARK: - Components
struct Trait: Codable, Identifiable {
    let id: Int
    let name: String
}

struct Skill: Codable, Identifiable {
    let id: Int
    let num: Int? // Skill 1, 2, 3
    let name: String
    let detail: String? // Short description
    let icon: String?
    let coolDown: [Int]? // [7, 7, ..., 5] for levels 1-10
    
    // If functions are needed for detailed values:
    let functions: [Function]?
}

struct NoblePhantasm: Codable, Identifiable {
    let id: Int
    let num: Int
    let name: String
    let rank: String
    let type: String // "Buster", etc
    let detail: String?
    let npGain: NPGain? // Hidden stat for NP
    
    // Detailed effects
    let functions: [Function]?
}

struct NPGain: Codable {
    let buster: [Int]?
    let arts: [Int]?
    let quick: [Int]?
    let extra: [Int]?
    let defence: [Int]?
    let np: [Int]?
}

struct Function: Codable {
    let funcId: Int
    let funcType: String?
    let funcTargetTeam: String?
    let funcTargetType: String?
    // "svals" contains the actual numerical values per level
    let svals: [vals]?
}

struct vals: Codable {
    let Rate: Int?
    let Value: Int?
    // Add other fields as necessary from Atlas API
}
