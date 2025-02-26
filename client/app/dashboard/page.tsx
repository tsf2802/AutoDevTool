
const Card = ({ title, description, image }: { title: string, description: string, image: string }) => {
    return (
        <div>
            <div className="bg-white shadow-md rounded-md p-4">
                <img src={image} alt={title} className="w-full h-64 object-cover rounded-md" />
                <h1 className="text-xl font-semibold mt-2">{title}</h1>
                <p className="text-gray-500 mt-2">{description}</p>
            </div>
        </div>
    )
}

const PROJECTS = [
    "djangoproject"
]

export default function Dashboard() {
    return (
        <div className="p-4">
            <section id="main" className="max-w-7xl mx-auto">
                <input type="text" id="search" placeholder="Search" className="w-full p-2 border border-gray-300 rounded-md" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {PROJECTS.map((project: string, index: number) => (
                        <Card key={index} title={project} description="A description" image="https://via.placeholder.com/150" />
                    ))}
                </div>
            </section>
        </div>
    )
}