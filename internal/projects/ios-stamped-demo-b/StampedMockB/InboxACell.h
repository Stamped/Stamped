//
//  InboxACell.h
//  StampedMockB
//
//  Created by Kevin Palms on 6/27/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface InboxACell : UITableViewCell {
  UILabel *cellTitle;
  UILabel *cellSubtitle;
  UIImageView *cellAvatar;
  UIImageView *cellStamp;
  NSString *userID;
  UIImageView *cellPhotoTag;
}

@property (retain) UILabel *cellTitle;
@property (retain) UILabel *cellSubtitle;
@property (retain) UIImageView *cellAvatar;
@property (retain) UIImageView *cellStamp;
@property (retain) NSString *userID;

- (id) initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier;
- (void) formatStamp;
- (void) showPhotoTag:(BOOL)tagged;

@end
