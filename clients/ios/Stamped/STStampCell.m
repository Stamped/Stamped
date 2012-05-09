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
#import "STConfiguration.h"
#import <QuartzCore/QuartzCore.h>

@implementation STStampCell

//Positions
static NSString* const _normalCellHeightKey = @"STStampCell.normalCellHeight";
static NSString* const _previewsDeltaHeightKey = @"STStampCell.previewsDeltaHeight";
static NSString* const _userImageOriginKey = @"STStampCell.userImageOrigin";
static NSString* const _headerTextOriginKey = @"STStampCell.headerTextOrigin";
static NSString* const _titleTextOriginKey = @"STStampCell.titleTextOrigin";
static NSString* const _categoryIconOriginKey = @"STStampCell.categoryIconOrigin";
static NSString* const _subtitleTextOriginKey = @"STStampCell.subtitleTextOrigin";
static NSString* const _dateTextTopRightKey = @"STStampCell.dateTextTopRight";
static NSString* const _previewsOriginKey = @"STStampCell.previewsOrigin";
static NSString* const _rightPaddingKey = @"STStampCell.rightPadding";

//Fonts
static NSString* const _headerUserFontKey = @"STStampCell.headerUserFont";
static NSString* const _headerVerbFontKey = @"STStampCell.headerVerbFont";
static NSString* const _titleFontKey = @"STStampCell.titleFont";
static NSString* const _dateFontKey = @"STStampCell.dateFont";
static NSString* const _subtitleFontKey = @"STStampCell.subtitleFont";

//Colors
static NSString* const _headerUserColorKey = @"STStampCell.headerUserColor";
static NSString* const _headerVerbColorKey = @"STStampCell.headerVerbColor";
static NSString* const _titleColorKey = @"STStampCell.titleColor";
static NSString* const _dateColorKey = @"STStampCell.dateColor";
static NSString* const _subtitleColorKey = @"STStampCell.subtitleColor";
static NSString* const _gradientTopColorKey = @"STStampCell.gradientTopColor";
static NSString* const _gradientBottomColorKey = @"STStampCell.gradientBottomColor";


+ (CGFloat)heightForStamp:(id<STStamp>)stamp {
  CGFloat defaultHeight = [[STConfiguration value:_normalCellHeightKey] floatValue];
  if (stamp) {
    if ([STPreviewsView previewHeightForStamp:stamp andMaxRows:1] > 0) {
      defaultHeight += [[STConfiguration value:_previewsDeltaHeightKey] floatValue];
    }
  }
  return defaultHeight;
}

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGFloat width = [Util standardFrameWithNavigationBar:YES].size.width;
    self.frame = CGRectMake(0, 0, width, [STStampCell heightForStamp:stamp]);
    CGFloat rightPadding = [[STConfiguration value:_rightPaddingKey] floatValue];
    // User Image
    CGPoint userImageOrigin = [[STConfiguration value:_userImageOriginKey] CGPointValue];
    UIView* imageView = [Util profileImageViewForUser:stamp.user withSize:STProfileImageSize46];
    [Util reframeView:imageView withDeltas:CGRectMake(userImageOrigin.x, userImageOrigin.y, 0, 0)];
    [self addSubview:imageView];
    
    
    // Title
    CGPoint titleOrigin = [[STConfiguration value:_titleTextOriginKey] CGPointValue];
    UIFont* titleFont = [STConfiguration value:_titleFontKey];
    UIView* titleView = [Util viewWithText:stamp.entity.title
                                      font:titleFont
                                     color:[STConfiguration value:_titleColorKey]
                                      mode:UILineBreakModeTailTruncation
                                andMaxSize:CGSizeMake(width - (titleOrigin.x + rightPadding), [Util lineHeightForFont:titleFont])];
    [Util reframeView:titleView withDeltas:CGRectMake(titleOrigin.x, titleOrigin.y, 0, 0)];
    [self addSubview:titleView];
    UIImage* stampImage = [Util stampImageForUser:stamp.user withSize:STStampImageSize18];
    UIImageView* stampView = [[[UIImageView alloc] initWithImage:stampImage] autorelease];
    [Util reframeView:stampView withDeltas:CGRectMake(CGRectGetMaxX(titleView.frame) - 6, titleView.frame.origin.y - 1, 0, 0)];
    [self addSubview:stampView];
    
    // Header text
    CGPoint headerOrigin = [[STConfiguration value:_headerTextOriginKey] CGPointValue];
    UIView* userNameView = [Util viewWithText:stamp.user.screenName
                                         font:[STConfiguration value:_headerUserFontKey]
                                        color:[STConfiguration value:_headerUserColorKey]
                                         mode:UILineBreakModeTailTruncation
                                   andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:userNameView withDeltas:CGRectMake(headerOrigin.x, headerOrigin.y, 0, 0)];
    [self addSubview:userNameView];
    UIView* verbPhraseView = [Util viewWithText:[NSString stringWithFormat:@" stamped a %@", stamp.entity.subcategory] //Improve
                                           font:[STConfiguration value:_headerVerbFontKey]
                                          color:[STConfiguration value:_headerVerbColorKey]
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:verbPhraseView withDeltas:CGRectMake(CGRectGetMaxX(userNameView.frame), headerOrigin.y, 0, 0)];
    [self addSubview:verbPhraseView];
    
    //Date text
    CGPoint dateTopRight = [[STConfiguration value:_dateTextTopRightKey] CGPointValue];
    NSString* dateString = [Util userReadableTimeSinceDate:stamp.created];
    UIView* dateView = [Util viewWithText:dateString
                                     font:[STConfiguration value:_dateFontKey]
                                    color:[STConfiguration value:_dateColorKey]
                                     mode:UILineBreakModeTailTruncation
                               andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:dateView withDeltas:CGRectMake(dateTopRight.x - dateView.frame.size.width, dateTopRight.y, 0, 0)];
    [self addSubview:dateView];
    
    // Footer text and category image
    CGPoint categoryImageOrigin = [[STConfiguration value:_categoryIconOriginKey] CGPointValue];
    UIImage* categoryImage = [Util imageForCategory:stamp.entity.category];
    UIImageView* categoryView = [[[UIImageView alloc] initWithImage:categoryImage] autorelease];
    [Util reframeView:categoryView withDeltas:CGRectMake(categoryImageOrigin.x, categoryImageOrigin.y, 0, 0)];
    [self addSubview:categoryView];
    
    CGPoint subtitleOrigin = [[STConfiguration value:_subtitleTextOriginKey] CGPointValue];
    UIView* footerTextView = [Util viewWithText:stamp.entity.subtitle
                                           font:[STConfiguration value:_subtitleFontKey]
                                          color:[STConfiguration value:_subtitleColorKey]
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:CGSizeMake(width - (subtitleOrigin.x + rightPadding), CGFLOAT_MAX)];
    [Util reframeView:footerTextView withDeltas:CGRectMake(subtitleOrigin.x, subtitleOrigin.y, 0, 0)];
    [self addSubview:footerTextView];
    
    if ([STPreviewsView previewHeightForStamp:stamp andMaxRows:1] > 0) {
      CGPoint previewsOrigin = [[STConfiguration value:_previewsOriginKey] CGPointValue];
      STPreviewsView* previewsView = [[[STPreviewsView alloc] initWithStamp:stamp andMaxRows:1] autorelease];
      [Util reframeView:previewsView withDeltas:CGRectMake(previewsOrigin.x, previewsOrigin.y, 0, 0)];
      [self addSubview:previewsView];
    }
    [Util addGradientToLayer:self.layer 
                  withColors:[NSArray arrayWithObjects:
                              [STConfiguration value:_gradientTopColorKey],
                              [STConfiguration value:_gradientBottomColorKey],
                              nil]
                    vertical:YES];
    self.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
  }
  return self;
}


- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
  [super setSelected:selected animated:animated];
  
  // Configure the view for the selected state
}

+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
  NSArray* images = [STPreviewsView imagesForPreviewWithStamp:stamp andMaxRows:1];
  NSMutableArray* allImages = [NSMutableArray arrayWithObject:[Util profileImageURLForUser:stamp.user withSize:STProfileImageSize46]];
  [allImages addObjectsFromArray:images];
  return [STCancellation loadImages:allImages withCallback:block];
}

+ (void)setupConfigurations {
  [STConfiguration addNumber:[NSNumber numberWithFloat:91] forKey:_normalCellHeightKey];
  [STConfiguration addNumber:[NSNumber numberWithFloat:45] forKey:_previewsDeltaHeightKey];
  [STConfiguration addPoint:[NSValue valueWithCGPoint:CGPointMake(11, 10)] forKey:_userImageOriginKey];
  [STConfiguration addPoint:[NSValue valueWithCGPoint:CGPointMake(69, 12)] forKey:_headerTextOriginKey];
  [STConfiguration addPoint:[NSValue valueWithCGPoint:CGPointMake(69, 27)] forKey:_titleTextOriginKey];
  [STConfiguration addPoint:[NSValue valueWithCGPoint:CGPointMake(69, 64)] forKey:_categoryIconOriginKey];
  [STConfiguration addPoint:[NSValue valueWithCGPoint:CGPointMake(85, 63.5)] forKey:_subtitleTextOriginKey];
  [STConfiguration addPoint:[NSValue valueWithCGPoint:CGPointMake(304, 12)] forKey:_dateTextTopRightKey];
  [STConfiguration addNumber:[NSNumber numberWithFloat:16] forKey:_rightPaddingKey];
  [STConfiguration addPoint:[NSValue valueWithCGPoint:CGPointMake(70, 95)] forKey:_previewsOriginKey];
  
  //Fonts
  [STConfiguration addFont:[UIFont stampedBoldFontWithSize:9] forKey:_headerUserFontKey];
  [STConfiguration addFont:[UIFont stampedFontWithSize:9] forKey:_headerVerbFontKey];
  [STConfiguration addFont:[UIFont stampedTitleLightFontWithSize:35] forKey:_titleFontKey];
  [STConfiguration addFont:[UIFont stampedFontWithSize:9] forKey:_dateFontKey];
  [STConfiguration addFont:[UIFont stampedFontWithSize:9] forKey:_subtitleFontKey];
  
  //Colors
  [STConfiguration addColor:[UIColor stampedGrayColor] forKey:_headerUserColorKey];
  [STConfiguration addColor:[UIColor stampedGrayColor] forKey:_headerVerbColorKey];
  [STConfiguration addColor:[UIColor stampedBlackColor] forKey:_titleColorKey];
  [STConfiguration addColor:[UIColor stampedGrayColor] forKey:_dateColorKey];
  [STConfiguration addColor:[UIColor stampedGrayColor] forKey:_subtitleColorKey];
  
  [STConfiguration addColor:[UIColor colorWithRed:.99 green:.99 blue:.99 alpha:1] forKey:_gradientTopColorKey];
  [STConfiguration addColor:[UIColor colorWithRed:.90 green:.90 blue:.90 alpha:1] forKey:_gradientBottomColorKey];
  
}

@end
