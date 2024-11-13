import { useState } from 'react';

import * as S from '@features/deploy/ui/api/api.style'

import InfoContainer from '@features/deploy/ui/common/deploy-info';
import ApiList from '@features/deploy/ui/api/api-list';
import Pagination from '@shared/ui/pagination/pagination';
import { useApiLists } from '@features/deploy/api/use-api.query';

const Api = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(5);
  const { data: apiData } = useApiLists(currentPage - 1, pageSize);

  return (
    <S.Container>
      <S.TopSection>
        <InfoContainer />
      </S.TopSection>
      <S.List>
        <ApiList apis={apiData?.apis || []} page={currentPage} />
        <Pagination
          currentPage={currentPage}
          totalPages={apiData?.totalPages || 0}
          onPageChange={setCurrentPage}
        />
      </S.List>
    </S.Container>
  )
};

export default Api;
