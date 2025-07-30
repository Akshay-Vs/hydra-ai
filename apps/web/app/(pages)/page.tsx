import InfoBlock from '@/components/sections/info-block';
import LiveTail from '@/components/sections/live-tail';
import { RequestProcessed } from '@/components/sections/request-processed';
import Block from '@/components/wrappers/block';

export default function Home() {
  return (
    <div className="col-center gap-4  pt-4">
      <div className="w-full center gap-4 h-[45vh]">
        <Block className="w-[80%] bg-transparent border-none">Graph 1 </Block>
        <Block className="w-[20%] bg-transparent border-none h-full p-0">
          <InfoBlock />
        </Block>
      </div>

      <div className="w-full center gap-4 h-[45vh]">
        <Block>
          <LiveTail />
        </Block>
        <Block>
          <RequestProcessed />
        </Block>
      </div>
    </div>
  );
}
