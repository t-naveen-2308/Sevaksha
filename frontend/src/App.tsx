import { ToastContainer } from "react-toastify";
import { useState } from "react";
import BrowserRouterProvider from "./BrowserRouterProvider";

function App() {

    const [toastStyle, setToastStyle] = useState<{
        backgroundColor: string;
        color: string;
    }>(
        { backgroundColor: "#ffffff", color: "#1f2937" }
    );
    setToastStyle({ backgroundColor: "#ffffff", color: "#1f2937" });;
    

    return (
        <>
            <div>
                <ToastContainer toastStyle={toastStyle} position="top-center" />
                <BrowserRouterProvider />
            </div>
        </>
    );
}

export default App;
