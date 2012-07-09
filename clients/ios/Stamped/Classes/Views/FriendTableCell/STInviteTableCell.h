//
//  STInviteTableCell.h
//  Stamped
//
//  Created by Landon Judkins on 7/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STContact.h"

@protocol STInviteTableCellDelegate;

@interface STInviteTableCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier;

- (void)setupWithContact:(STContact*)contact;

@property(nonatomic, readwrite, assign) id<STInviteTableCellDelegate> delegate;
@property (nonatomic, readonly, retain) STContact* contact;

@end

@protocol STInviteTableCellDelegate

- (void)inviteTableCellToggleInvite:(STInviteTableCell*)cell;

@end
