import LiveTail from '@/components/sections/live-tail';
import Block from '@/components/wrappers/block';

export default function Home() {
  return (
    <div className="col-center gap-4  pt-4">
      <div className="w-full center gap-4 h-[45vh]">
        <Block className="w-[80%] bg-transparent border-none">Graph 1 </Block>
        <Block className="w-[20%]">Info</Block>
      </div>

      <div className="w-full center gap-4 h-[45vh]">
        <Block>
          <LiveTail />
        </Block>
        <Block>Graph 2</Block>
      </div>
    </div>
  );
}
