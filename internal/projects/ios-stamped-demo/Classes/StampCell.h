//
//  StampCell.h
//  Stamped
//
//  Created by Kevin Palms on 2/9/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface StampCell : UITableViewCell {
	UILabel	*stampCellTitle;
	UILabel	*stampCellUsers;
	UILabel	*stampCellType;
	UILabel	*stampCellDate;
	UIImageView *stampCellImage;
}

@property (retain) UILabel *stampCellTitle;
@property (retain) UILabel *stampCellUsers;
@property (retain) UILabel *stampCellType;
@property (retain) UILabel *stampCellDate;
@property (retain) UIImageView *stampCellImage;

+ (UIImage *)imageThumbnailForStampId:(NSNumber *)stampId;
+ (NSString *)timestampFromDateStamped:(NSDate *)dateStamped;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier;

@end
