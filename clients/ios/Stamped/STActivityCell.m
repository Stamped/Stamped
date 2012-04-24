//
//  STActivityCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActivityCell.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

@interface STActivityCell ()

+ (CGFloat)headerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)bodyHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)imagesHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)footerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (UIFont*)headerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (UIFont*)bodyFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (UIFont*)footerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (CGRect)headerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGRect)bodyBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGRect)footerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (CGFloat)topPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)bottomPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)xOffsetForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)textWidthForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;


@end

@implementation STActivityCell

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"test"];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGFloat height = [STActivityCell heightForCellWithActivity:activity andScope:scope];
    UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, [Util fullscreenFrame].size.width, height)] autorelease];
    if (scope == STStampedAPIScopeYou) {
      
    }
    else {
      if (activity.subjects.count > 0) {
        id<STUser> subject = [activity.subjects objectAtIndex:0];
        UIView* imageView = [Util profileImageViewForUser:subject withSize:STProfileImageSize31];
        [Util reframeView:imageView withDeltas:CGRectMake(([STActivityCell xOffsetForActivity:activity andScope:scope] - STProfileImageSize31)/2, 8, 0, 0)];
        [view addSubview:imageView];
      }
    }
    if (activity.header) {
      CGRect headerBounds = [STActivityCell headerBoundsForActivity:activity andScope:scope];
      UIView* headerView = [Util viewWithText:activity.header
                                         font:[STActivityCell headerFontForActivity:activity andScope:scope]
                                        color:activity.body ? [UIColor stampedGrayColor] : [UIColor stampedDarkGrayColor]
                                         mode:UILineBreakModeWordWrap
                                   andMaxSize:headerBounds.size];
      headerView.frame = CGRectOffset(headerView.frame, headerBounds.origin.x, headerBounds.origin.y);
      [view addSubview:headerView];
    }
    if (activity.body) {
      CGRect bodyBounds = [STActivityCell bodyBoundsForActivity:activity andScope:scope];
      UIView* bodyView = [Util viewWithText:activity.body
                                       font:[STActivityCell bodyFontForActivity:activity andScope:scope]
                                      color:[UIColor stampedDarkGrayColor]
                                       mode:UILineBreakModeWordWrap
                                 andMaxSize:bodyBounds.size];
      bodyView.frame = CGRectOffset(bodyView.frame, bodyBounds.origin.x, bodyBounds.origin.y);
      [view addSubview:bodyView];
    }
    CGRect footerBounds = [STActivityCell footerBoundsForActivity:activity andScope:scope];
    UIView* dateView = [Util viewWithText:[Util shortUserReadableTimeSinceDate:activity.created] 
                                     font:[STActivityCell footerFontForActivity:activity andScope:scope]
                                    color:[UIColor stampedLightGrayColor]
                                     mode:UILineBreakModeClip
                               andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:dateView withDeltas:CGRectMake(footerBounds.origin.x, footerBounds.origin.y, 0, 0)];
    [view addSubview:dateView];
    if (activity.footer) {
      footerBounds.origin.x = CGRectGetMaxX(dateView.frame) + 5;
      footerBounds.size.width -= footerBounds.origin.x - dateView.frame.origin.x;
      UIView* footerView = [Util viewWithText:activity.footer
                                         font:[STActivityCell footerFontForActivity:activity andScope:scope]
                                        color:[UIColor stampedLightGrayColor]
                                         mode:UILineBreakModeWordWrap
                                   andMaxSize:footerBounds.size];
      [Util reframeView:footerView withDeltas:CGRectMake(footerBounds.origin.x, footerBounds.origin.y, 0, 0)];
      [view addSubview:footerView];
    }
    [self.contentView addSubview:view];
  }
  return self;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
  [super setSelected:selected animated:animated];
}

+ (CGFloat)heightForCellWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  CGFloat height = 0;
  height += [STActivityCell topPaddingForActivity:activity andScope:scope];
  height += [STActivityCell headerHeightForActivity:activity andScope:scope];
  height += [STActivityCell bodyHeightForActivity:activity andScope:scope];
  height += [STActivityCell imagesHeightForActivity:activity andScope:scope];
  height += [STActivityCell footerHeightForActivity:activity andScope:scope];
  height += [STActivityCell bottomPaddingForActivity:activity andScope:scope];
  return height;
}

+ (CGFloat)headerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (activity.header) {
    CGSize size = [Util sizeWithText:activity.header 
                                font:[STActivityCell headerFontForActivity:activity andScope:scope]
                                mode:UILineBreakModeWordWrap
                          andMaxSize:[STActivityCell headerBoundsForActivity:activity andScope:scope].size];
    return size.height;
  }
  else {
    return 0;
  }
}

+ (CGFloat)bodyHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (activity.body) {
    return [Util sizeWithText:activity.body 
                         font:[STActivityCell bodyFontForActivity:activity andScope:scope]
                         mode:UILineBreakModeWordWrap
                   andMaxSize:[STActivityCell bodyBoundsForActivity:activity andScope:scope].size].height;
  }
  else {
    return 0;
  }
}

+ (CGFloat)imagesHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (scope == STStampedAPIScopeYou) {
    if (activity.subjects.count > 1) {
      return 31;
    }
    else {
      return 0;
    }
  }
  else {
    if (activity.objects.users.count > 1) {
      return 31;
    }
    else {
      return 0;
    }
  }
}

+ (CGFloat)footerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [Util sizeWithText:@"Test" 
                       font:[STActivityCell footerFontForActivity:activity andScope:scope] 
                       mode:UILineBreakModeTailTruncation 
                 andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)].height;
}

+ (UIFont*)headerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (activity.body) {
  return [UIFont stampedFontWithSize:12];
  }
  else {
    return [UIFont stampedFontWithSize:14];
  }
}

+ (UIFont*)bodyFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [UIFont stampedFontWithSize:14];
}

+ (UIFont*)footerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [UIFont stampedFontWithSize:10];
}

+ (CGRect)headerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return CGRectMake([STActivityCell xOffsetForActivity:activity andScope:scope],
                    [STActivityCell topPaddingForActivity:activity andScope:scope], 
                    [STActivityCell textWidthForActivity:activity andScope:scope],
                    CGFLOAT_MAX);
}

+ (CGRect)bodyBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return CGRectMake([STActivityCell xOffsetForActivity:activity andScope:scope],
                    [STActivityCell headerBoundsForActivity:activity andScope:scope].origin.y + [STActivityCell headerHeightForActivity:activity andScope:scope], 
                    [STActivityCell textWidthForActivity:activity andScope:scope],
                    CGFLOAT_MAX);
}

+ (CGRect)footerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return CGRectMake([STActivityCell xOffsetForActivity:activity andScope:scope],
                    [STActivityCell bodyBoundsForActivity:activity andScope:scope].origin.y + [STActivityCell bodyHeightForActivity:activity andScope:scope], 
                    [STActivityCell textWidthForActivity:activity andScope:scope],
                    CGFLOAT_MAX);
}

+ (CGFloat)topPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return 5;
}

+ (CGFloat)bottomPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [STActivityCell topPaddingForActivity:activity andScope:scope];
}

+ (CGFloat)xOffsetForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return 60;
}

+ (CGFloat)textWidthForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [Util fullscreenFrame].size.width - ( [STActivityCell xOffsetForActivity:activity andScope:scope] + 20 );
}

@end
