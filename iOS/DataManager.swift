import Foundation
import SQLite // Assuming SQLite.swift

class DataManager {
    static let shared = DataManager()
    var db: Connection?
    
    init() {
        // Setup DB connection (path to bundle or document directory)
        do {
            let path = Bundle.main.path(forResource: "fgo_full_data_jp", ofType: "db")!
            db = try Connection(path, readonly: true)
        } catch {
            print("DB Connection Error: \(error)")
        }
    }
    
    func fetchServantDetail(id: Int) -> ServantDetail? {
        // Table Definition
        let servants = Table("servants")
        let colId = Expression<Int>("id")
        let colName = Expression<String>("name")
        let colJson = Expression<String>("json_data")
        
        do {
            // QUERY:
            // "SELECT * FROM servants WHERE id = ?"
            // We specifically need the JSON blob to parse the detailed models
            if let row = try db?.pluck(servants.filter(colId == id)) {
                let jsonString = row[colJson]
                
                // Parse JSON
                if let data = jsonString.data(using: .utf8) {
                    let decoder = JSONDecoder()
                    let detail = try decoder.decode(ServantDetail.self, from: data)
                    return detail
                }
            }
        } catch {
            print("Query Error: \(error)")
        }
        return nil
    }
}
