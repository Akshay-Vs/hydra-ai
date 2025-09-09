'use client';
import Block from '../wrappers/block';
import AddThirdPartyButton from './add-third-party-button';
import MCPServerList from './mcp-servers-list';

const ThirdPartyIntegration = () => {
  return (
    <Block className="full col min-h-[28rem] !justify-start items-start relative">
      <div className="flex w-full justify-between pb-4">
        <h1 className="px-2 text-xl text-dull-dark font-medium p-2">Third Party Integrations</h1>
        <AddThirdPartyButton />
      </div>
      <MCPServerList />
    </Block>
  );
};

export default ThirdPartyIntegration;
