import SwiftUI

// MARK: - Main Detail View
struct ServantDetailView: View {
    let servant: ServantDetail
    @State private var selectedTab = 0
    
    // Chaldea Theme Colors
    let chaldeaBlue = Color(red: 0, green: 0.94, blue: 1.0) // #00f0ff
    let chaldeaDark = Color(red: 0.04, green: 0.06, blue: 0.13) // #0b1021
    
    var body: some View {
        ZStack {
            // Background
            chaldeaDark.ignoresSafeArea()
            
            // Grid Effect (Simple overlay)
            Image(systemName: "circle.grid.hex.fill") // Placeholder for hex grid
                .resizable()
                .opacity(0.05)
                .foregroundColor(chaldeaBlue)
            
            VStack(spacing: 0) {
                // Header (Name & Class)
                HStack {
                    Text(servant.name)
                        .font(.custom("HelveticaNeue-Bold", size: 24))
                        .foregroundColor(.white)
                        .shadow(color: chaldeaBlue, radius: 5)
                    
                    Spacer()
                    
                    Text(servant.className.uppercased())
                        .font(.caption)
                        .padding(6)
                        .background(chaldeaBlue.opacity(0.2))
                        .foregroundColor(chaldeaBlue)
                        .cornerRadius(4)
                        .overlay(
                            RoundedRectangle(cornerRadius: 4)
                                .stroke(chaldeaBlue, lineWidth: 1)
                        )
                }
                .padding()
                .background(Color.black.opacity(0.3))
                
                // Tabs
                HStack(spacing: 0) {
                    TabButton(title: "STATUS", isSelected: selectedTab == 0) { selectedTab = 0 }
                    TabButton(title: "SKILL / NP", isSelected: selectedTab == 1) { selectedTab = 1 }
                    TabButton(title: "HIDDEN", isSelected: selectedTab == 2) { selectedTab = 2 }
                }
                .padding(.vertical, 10)
                
                // Content
                ScrollView {
                    if selectedTab == 0 {
                        StatusTabView(servant: servant, accentColor: chaldeaBlue)
                    } else if selectedTab == 1 {
                        SkillNPTabView(servant: servant, accentColor: chaldeaBlue)
                    } else {
                        HiddenStatsTabView(servant: servant, accentColor: chaldeaBlue)
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}

// MARK: - Tab Button Component
struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.custom("HelveticaNeue-Medium", size: 14))
                .foregroundColor(isSelected ? .black : .white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(isSelected ? Color(red: 0, green: 0.94, blue: 1.0) : Color.clear)
                .overlay(
                    Rectangle()
                        .stroke(Color(red: 0, green: 0.94, blue: 1.0), lineWidth: 1)
                )
        }
    }
}

// MARK: - Tab 1: STATUS
struct StatusTabView: View {
    let servant: ServantDetail
    let accentColor: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Stats Row
            HStack(spacing: 20) {
                StatBox(label: "MAX HP", value: "\(servant.hpMax)", color: accentColor)
                StatBox(label: "MAX ATK", value: "\(servant.atkMax)", color: accentColor)
            }
            
            Divider().background(accentColor)
            
            // Traits
            Text("/// TRAITS")
                .font(.caption)
                .foregroundColor(accentColor)
            
            FlowLayout(mode: .scrollable, items: servant.traits, itemSpacing: 5) { trait in
                Text(trait.name)
                    .font(.caption2)
                    .padding(6)
                    .background(Color.white.opacity(0.1))
                    .cornerRadius(4)
                    .foregroundColor(.white)
                    .overlay(
                        RoundedRectangle(cornerRadius: 4)
                            .stroke(Color.white.opacity(0.3), lineWidth: 1)
                    )
            }
        }
        .padding()
    }
}

struct StatBox: View {
    let label: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading) {
            Text(label)
                .font(.caption2)
                .foregroundColor(color)
            Text(value)
                .font(.title2).bold()
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.white.opacity(0.05))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8).stroke(color.opacity(0.5), lineWidth: 1)
        )
    }
}

// MARK: - Tab 2: SKILL / NP
struct SkillNPTabView: View {
    let servant: ServantDetail
    let accentColor: Color
    @State private var isStrengthened = false // Toggle for upgrade
    
    var body: some View {
        VStack(spacing: 20) {
            Toggle("INCLUDE UPGRADES", isOn: $isStrengthened)
                .padding()
                .background(Color.white.opacity(0.05))
                .cornerRadius(8)
                .foregroundColor(accentColor)
                .padding(.horizontal)
            
            ForEach(servant.skills) { skill in
                SkillCard(skill: skill, accentColor: accentColor)
            }
            
            Text("/// NOBLE PHANTASM")
                .font(.headline)
                .foregroundColor(accentColor)
                .padding(.top)
                
            ForEach(servant.noblePhantasms) { np in
                NPCard(np: np, accentColor: accentColor)
            }
        }
    }
}

struct SkillCard: View {
    let skill: Skill
    let accentColor: Color
    
    var body: some View {
        VStack(alignment: .leading) {
            HStack {
                // Icon placeholder
                Image(systemName: "diamond.fill")
                    .foregroundColor(accentColor)
                Text(skill.name)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                if let cd = skill.coolDown, let min = cd.first {
                    Text("CT \(min)")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
            
            if let detail = skill.detail {
                Text(detail)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                    .padding(.top, 5)
            }
        }
        .padding()
        .background(Color.black.opacity(0.5))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8).stroke(accentColor.opacity(0.3), lineWidth: 1)
        )
        .padding(.horizontal)
    }
}

struct NPCard: View {
    let np: NoblePhantasm
    let accentColor: Color
    
    var body: some View {
        VStack(alignment: .leading) {
            HStack {
                Text(np.type.uppercased()) // "BUSTER" etc
                    .font(.caption)
                    .bold()
                    .padding(4)
                    .background(Color.red.opacity(0.7)) // Dynamic color based on type
                    .cornerRadius(4)
                
                Text(np.name)
                    .bold()
                    .foregroundColor(.white)
            }
            .padding(.bottom, 5)
            
            if let detail = np.detail {
                Text(detail)
                    .font(.callout)
                    .foregroundColor(accentColor) // Neon text for values
            }
        }
        .padding()
        .background(
            LinearGradient(gradient: Gradient(colors: [Color.black, Color.blue.opacity(0.2)]), startPoint: .leading, endPoint: .trailing)
        )
        .cornerRadius(8)
        .padding(.horizontal)
    }
}

// MARK: - Tab 3: HIDDEN STATS
struct HiddenStatsTabView: View {
    let servant: ServantDetail
    let accentColor: Color
    
    var body: some View {
        VStack(spacing: 25) {
            Text("/// SPIRIT ORIGIN HIDDEN PARAMETERS")
                .font(.caption)
                .foregroundColor(accentColor)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal)
            
            // NP Gain (Arts) - Mockup value
            StatGauge(label: "NP GAIN (Arts)", value: 0.65, maxValue: 2.0, accentColor: accentColor)
            
            // Star Weight
            StatGauge(label: "STAR WEIGHT", value: Double(servant.starAbsorb ?? 100), maxValue: 250, accentColor: accentColor)
            
            // Star Gen
            StatGauge(label: "STAR GEN", value: Double(servant.starGen ?? 10), maxValue: 50, accentColor: accentColor)
            
            // Gemini Strategy Tip
            HStack(alignment: .top) {
                Image(systemName: "cpu")
                    .foregroundColor(accentColor)
                    .font(.largeTitle)
                
                VStack(alignment: .leading) {
                    Text("TRISMEGISTUS Ⅱ ANALYSIS")
                        .font(.caption)
                        .bold()
                        .foregroundColor(accentColor)
                    
                    Text("有効特攻: 人属性特攻 / 弱点クラス: アーチャー\n対策: 必中礼装を推奨")
                        .font(.custom("Courier", size: 14))
                        .foregroundColor(.white)
                        .padding(.top, 2)
                }
            }
            .padding()
            .background(Color.white.opacity(0.05))
            .cornerRadius(12)
            .padding()
        }
        .padding(.top)
    }
}

struct StatGauge: View {
    let label: String
    let value: Double
    let maxValue: Double
    let accentColor: Color
    
    var body: some View {
        VStack(alignment: .leading) {
            HStack {
                Text(label)
                    .foregroundColor(.gray)
                    .font(.caption)
                Spacer()
                Text(String(format: "%.2f", value))
                    .foregroundColor(accentColor)
                    .font(.headline)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .frame(width: geometry.size.width, height: 8)
                        .opacity(0.3)
                        .foregroundColor(.gray)
                    
                    Rectangle()
                        .frame(width: min(CGFloat(value / maxValue) * geometry.size.width, geometry.size.width), height: 8)
                        .foregroundColor(accentColor)
                        .shadow(color: accentColor, radius: 5) // Glow
                }
                .cornerRadius(4)
            }
            .frame(height: 8)
        }
        .padding(.horizontal)
    }
}

// Simple FlowLayout Helper (Placeholder for actual implementation)
struct FlowLayout<Data: RandomAccessCollection, Content: View>: View where Data.Element: Identifiable {
    let mode: Mode
    let items: Data
    let itemSpacing: CGFloat
    let content: (Data.Element) -> Content
    
    enum Mode { case scrollable }

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: itemSpacing) {
                ForEach(items) { item in
                    content(item)
                }
            }
        }
        .padding(.horizontal)
    }
}
