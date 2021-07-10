import React from 'react';
import { Modal } from 'office-ui-fabric-react/lib/Modal';
// import { Link } from 'office-ui-fabric-react/lib/Link';
import {getTheme, IconButton } from 'office-ui-fabric-react';
import {getContentStyles, getIconButtonStyles} from './styles/modal';
import config from './services/config';

import './ChangeLogModal.css';

const TITLE_ID = 'ChangeLogTitle';
const SUB_TITLE_ID = 'ChangeLogSubtitle';

interface ChangeLogModalProps {
    isOpen: boolean
    onClose: () => void
}

export default function ChangeLogModal(props: ChangeLogModalProps) {
    const theme = getTheme();
    const contentStyles = getContentStyles(theme);
    const iconButtonStyles = getIconButtonStyles(theme);

    return (
        <Modal
            titleAriaId={TITLE_ID}
            subtitleAriaId={SUB_TITLE_ID}
            isOpen={props.isOpen}
            onDismiss={props.onClose}
            containerClassName={contentStyles.container}
        >
            <div className={contentStyles.header}>
                <span id={TITLE_ID}>Changelog for {config.appVersion}</span>
                <IconButton
                    iconProps={{ iconName: 'Cancel' }}
                    styles={iconButtonStyles}
                    ariaLabel='Close popup modal'
                    onClick={props.onClose as any}
                />
            </div>
        </Modal>
    )
}

ChangeLogModal.defaultProps = {isOpen: false};