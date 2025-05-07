import Image from "next/image";
import InputFields from "./_components/InputFields";

export default function Home() {
  return (
    <div className='bg-gray-200 h-screen flex px-20 md:px-32 lg:px-48 xl:px-60'>
      <div className="text-black my-5 bg-white w-full rounded-lg py-5 px-10 overflow-y-scroll">
        <InputFields/>
      </div>
    </div>
  );
}
