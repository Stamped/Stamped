//
//  InboxACell.m
//  StampedMockB
//
//  Created by Kevin Palms on 6/27/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "InboxACell.h"


@implementation InboxACell

@synthesize cellAvatar, cellStamp, cellTitle, cellSubtitle, userID;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier
{
  self = [super initWithStyle:style reuseIdentifier:reuseIdentifier];
  if (self) {
    // Initialization code
    
		UIView *cellView = self.contentView;
    
    // STAMP
    cellStamp = [[UIImageView alloc] initWithFrame:CGRectMake(67, 8, 19, 19)];
    [cellStamp setBackgroundColor:[UIColor clearColor]];
		[cellView addSubview:cellStamp];
    
    
		// TITLE
		cellTitle = [[UILabel alloc] initWithFrame:CGRectMake(67, 8, [[UIScreen mainScreen] applicationFrame].size.width - 105, 59)];
		[cellTitle setTextColor:[UIColor colorWithRed:0 green:0 blue:0 alpha:0.65882]];
		[cellTitle setHighlightedTextColor:[UIColor whiteColor]];
		[cellTitle setBackgroundColor:[UIColor clearColor]];
		cellTitle.font = [UIFont fontWithName:@"TGLight" size:47];
    cellTitle.numberOfLines = 1;
		[cellView addSubview:cellTitle];
		//[cellTitle release];
    
    // AVATAR
    cellAvatar = [[UIImageView alloc] initWithFrame:CGRectMake(15, 8, 39, 39)];
    [cellAvatar setBackgroundColor:[UIColor clearColor]];
		[cellView addSubview:cellAvatar];
    
    // SUBTITLE
    cellSubtitle = [[UILabel alloc] initWithFrame:CGRectMake(69, 58, [[UIScreen mainScreen] applicationFrame].size.width - 85, 12)];
		[cellSubtitle setTextColor:[UIColor colorWithRed:0.6 green:0.6 blue:0.6 alpha:1]];
    [cellSubtitle setBackgroundColor:[UIColor clearColor]];
		cellSubtitle.font = [UIFont systemFontOfSize:12];
    cellSubtitle.numberOfLines = 1;
		[cellView addSubview:cellSubtitle];
    
    // PHOTO TAG
    cellPhotoTag = [[UIImageView alloc] initWithFrame:CGRectMake(69, 59, 12, 9)];
    cellPhotoTag.image = [UIImage imageNamed:@"has-photo.png"];
    [self.contentView addSubview:cellPhotoTag];
    
    // ARROW
    UIImageView *cellArrow = [[UIImageView alloc] initWithFrame:CGRectMake([[UIScreen mainScreen] applicationFrame].size.width - 22, 34, 8, 12)];
    cellArrow.image = [UIImage imageNamed:@"cell-arrow.png"];
    [cellView addSubview:cellArrow];
    [cellArrow release];
    
    cellView.backgroundColor = [UIColor colorWithPatternImage:[UIImage imageNamed:@"cell-bg.png"]];

  }
  return self;
}

- (void)formatStamp
{
  CGSize expectedLabelSize = [cellTitle.text sizeWithFont:[UIFont fontWithName:@"TGLight" size:47] 
                                        constrainedToSize:CGSizeMake([[UIScreen mainScreen] applicationFrame].size.width - 105, 59)  
                                            lineBreakMode:UILineBreakModeTailTruncation];
  
  self.cellStamp.frame = CGRectMake((expectedLabelSize.width + 60), 8, 19, 19);
  
}

- (void)showPhotoTag:(BOOL)tagged
{
  if (tagged) {
    [cellPhotoTag setHidden:NO];
    cellSubtitle.frame = CGRectMake(85, 58, [[UIScreen mainScreen] applicationFrame].size.width - 121, 12);
  }
  
  else {
    [cellPhotoTag setHidden:YES];
    cellSubtitle.frame = CGRectMake(69, 58, [[UIScreen mainScreen] applicationFrame].size.width - 85, 12);
  }
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
    [super setSelected:selected animated:animated];

    // Configure the view for the selected state
}

- (void)dealloc
{
  [cellTitle release];
  [cellSubtitle release];
  [cellStamp release];
  [cellAvatar release];
  [cellPhotoTag release];
  [super dealloc];
}

@end
