function Footer() {
    return (
        <>
            <footer
                className={
                    "section bg-footer " +
                    (localStorage.getItem("theme") &&
                    localStorage.getItem("theme") === "light"
                        ? "bg-base-200"
                        : "bg-base-300 ")
                }
            >
                <div className="flex justify-between px-16">
                    {/* Information Section */}
                    <div>
                        <h6
                            className={
                                "uppercase text-lg border-b mb-2 flex items-center gap-2 " +
                                (localStorage.getItem("theme") === "light"
                                    ? "border-gray-900"
                                    : "border-gray-300")
                            }
                        >
                            <span className="border rounded px-2 py-1 bg-gray-100">
                                <img
                                    src="https://static.vecteezy.com/system/resources/previews/005/747/906/non_2x/info-icon-template-information-icon-colorful-free-vector.jpg"
                                    alt="Info Icon"
                                    className="w-5 h-5"
                                />
                            </span>
                            Information
                        </h6>
                        <ul className="list-unstyled mt-1">
                            <li>
                                <a href="">Sections</a>
                            </li>
                            <li>
                                <a href="">Books</a>
                            </li>
                        </ul>
                    </div>

                    {/* Resources Section */}
                    <div>
                        <h6
                            className={
                                "uppercase text-lg border-b mb-2 flex items-center gap-2 " +
                                (localStorage.getItem("theme") === "light"
                                    ? "border-gray-900"
                                    : "border-gray-300")
                            }
                        >
                            <span className="border rounded px-2 py-1 bg-gray-100">
                                <img
                                    src="https://static.vecteezy.com/system/resources/previews/006/827/891/non_2x/global-icon-sign-symbol-logo-vector.jpg"
                                    alt="Resources Icon"
                                    className="w-6 h-5"
                                />
                            </span>
                            Resources
                        </h6>
                        <ul className="list-unstyled mt-2">
                            <li>
                                <a href="">Wikipedia</a>
                            </li>
                            <li>
                                <a href="">React Blog</a>
                            </li>
                        </ul>
                    </div>

                    {/* Contact Us Section */}
                    <div>
                        <h6
                            className={
                                "uppercase text-lg border-b mb-2 flex items-center gap-2 " +
                                (localStorage.getItem("theme") === "light"
                                    ? "border-gray-900"
                                    : "border-gray-300")
                            }
                        >
                            <span className="border rounded px-2 py-1 bg-gray-100">
                                <img
                                    src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTgtbXBp24msJxOeBDX9owrFPBmMlD6Ojn59w&s"
                                    alt="Contact Icon"
                                    className="w-5 h-5"
                                />
                            </span>
                            Contact Us
                        </h6>
                        <p className="mt-2">
                            Contact us for help
                        </p>
                        <p className="mt-1 font-semibold">+91 9398894023</p>
                    </div>

                    {/* Help and Support Section */}
                    <div>
                        <h6
                            className={
                                "uppercase text-lg border-b mb-2 flex items-center gap-2 " +
                                (localStorage.getItem("theme") === "light"
                                    ? "border-gray-900"
                                    : "border-gray-300")
                            }
                        >
                            <span className="border rounded px-2 py-1 bg-gray-100">
                                <img
                                    src="https://t4.ftcdn.net/jpg/01/58/21/69/360_F_158216984_zSFxdd273rSrPmwnsK1mwukR5c2N0zWq.jpg"
                                    alt="Help Icon"
                                    className="w-5 h-5"
                                />
                            </span>
                            Help and Support
                        </h6>
                        <ul className="list-unstyled mt-2">
                            <li>
                                <a href="">FAQs</a>
                            </li>
                            <li>
                                <a href="">Support Center</a>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Footer Bottom Text */}
                <div className="text-center mt-6 border-t pt-4">
                    <p>2025 © Sevaksha, All Rights Reserved</p>
                </div>
            </footer>
        </>
    );
}

export default Footer;