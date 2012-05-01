//
//  STStampCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampCell.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "TTTAttributedLabel.h"
#import "STPreviewsView.h"

@implementation STStampCell

+ (CGFloat)heightForStamp:(id<STStamp>)stamp {
  CGFloat defaultHeight = 91;
  if (stamp) {
    if ([STPreviewsView previewHeightForStamp:stamp andMaxRows:1] > 0) {
      defaultHeight += 45;
    }
  }
  return defaultHeight;
}

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGFloat width = 320;
    CGFloat textXOffset = 69;
    CGFloat textWidth = width - ( textXOffset + 11 );
    CGFloat leftPadding = 16;
    // User Image
    UIView* imageView = [Util profileImageViewForUser:stamp.user withSize:STProfileImageSize46];
    [Util reframeView:imageView withDeltas:CGRectMake(11, 10, 0, 0)];
    [self addSubview:imageView];
    
    
    // Title
    CGPoint titleOrigin = CGPointMake(69, 27);
    UIFont* titleFont = [UIFont stampedTitleFontLightWithSize:29];
    UIView* titleView = [Util viewWithText:stamp.entity.title
                                      font:titleFont
                                     color:[UIColor stampedBlackColor]
                                      mode:UILineBreakModeTailTruncation
                                andMaxSize:CGSizeMake(textWidth, [@"Test" sizeWithFont:titleFont].height)];
    [Util reframeView:titleView withDeltas:CGRectMake(titleOrigin.x, titleOrigin.y, 0, 0)];
    [self addSubview:titleView];
    UIImage* stampImage = [Util stampImageForUser:stamp.user withSize:STStampImageSize18];
    UIImageView* stampView = [[[UIImageView alloc] initWithImage:stampImage] autorelease];
    [Util reframeView:stampView withDeltas:CGRectMake(CGRectGetMaxX(titleView.frame) - 6, titleView.frame.origin.y - 1, 0, 0)];
    [self addSubview:stampView];
    
    // Header text
    CGFloat headerTextFontSize = 9;
    CGFloat headerYOffset = 12;
    UIView* userNameView = [Util viewWithText:stamp.user.screenName
                                         font:[UIFont stampedBoldFontWithSize:headerTextFontSize]
                                        color:[UIColor stampedGrayColor]
                                         mode:UILineBreakModeTailTruncation
                                   andMaxSize:CGSizeMake(textWidth, CGFLOAT_MAX)];
    [Util reframeView:userNameView withDeltas:CGRectMake(textXOffset, headerYOffset, 0, 0)];
    [self addSubview:userNameView];
    UIView* verbPhraseView = [Util viewWithText:[NSString stringWithFormat:@" stamped a %@", stamp.entity.subcategory] //Improve
                                           font:[UIFont stampedFontWithSize:headerTextFontSize]
                                          color:[UIColor stampedGrayColor]
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:verbPhraseView withDeltas:CGRectMake(CGRectGetMaxX(userNameView.frame), headerYOffset, 0, 0)];
    [self addSubview:verbPhraseView];
    
    //Date text
    NSString* dateString = [Util userReadableTimeSinceDate:stamp.created];
    UIView* dateView = [Util viewWithText:dateString
                                     font:[UIFont stampedFontWithSize:headerTextFontSize]
                                    color:[UIColor stampedGrayColor]
                                     mode:UILineBreakModeTailTruncation
                               andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:dateView withDeltas:CGRectMake(width - (leftPadding + dateView.frame.size.width), headerYOffset, 0, 0)];
    [self addSubview:dateView];
    
    // Footer text and category image
    CGPoint footerOrigin = CGPointMake(68, 64);
    UIImage* categoryImage = [Util imageForCategory:stamp.entity.category];
    UIImageView* categoryView = [[[UIImageView alloc] initWithImage:categoryImage] autorelease];
    [Util reframeView:categoryView withDeltas:CGRectMake(footerOrigin.x, footerOrigin.y, 0, 0)];
    [self addSubview:categoryView];
    CGFloat footerTextViewX = CGRectGetMaxX(categoryView.frame) + 5;
    UIView* footerTextView = [Util viewWithText:stamp.entity.subtitle
                                           font:[UIFont stampedFontWithSize:headerTextFontSize]
                                          color:[UIColor stampedGrayColor]
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:CGSizeMake(width - (footerTextViewX + leftPadding), CGFLOAT_MAX)];
    [Util reframeView:footerTextView withDeltas:CGRectMake(footerTextViewX, footerOrigin.y - .5, 0, 0)];
    [self addSubview:footerTextView];
    
    if ([STPreviewsView previewHeightForStamp:stamp andMaxRows:1] > 0) {
      STPreviewsView* previewsView = [[[STPreviewsView alloc] initWithStamp:stamp andMaxRows:1] autorelease];
      [Util reframeView:previewsView withDeltas:CGRectMake(70, 95, 0, 0)];
      [self addSubview:previewsView];
    }
  }
  return self;
}


- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
  [super setSelected:selected animated:animated];
  
  // Configure the view for the selected state
}

@end
