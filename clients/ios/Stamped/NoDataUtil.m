//
//  NoDataUtil.m
//  Stamped
//
//  Created by Landon Judkins on 7/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "NoDataUtil.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"

@implementation NoDataUtil

+ (UIView*)stampWatermarkWithTitle:(NSString*)title andSubtitle:(NSString*)subtitle {
    UIImageView* waterMark = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"watermark_nostamps"]] autorelease];
    UILabel* top = [Util viewWithText:title
                                 font:[UIFont stampedBoldFontWithSize:12]
                                color:[UIColor stampedGrayColor]
                                 mode:UILineBreakModeTailTruncation
                           andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    UILabel* bottom = [Util viewWithText:subtitle
                                    font:[UIFont stampedFontWithSize:12]
                                   color:[UIColor stampedGrayColor]
                                    mode:UILineBreakModeTailTruncation
                              andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    top.frame = [Util centeredAndBounded:top.frame.size inFrame:waterMark.frame];
    [Util reframeView:top withDeltas:CGRectMake(0, -7, 0, 0)];
    bottom.frame = [Util centeredAndBounded:bottom.frame.size inFrame:waterMark.frame];
    [Util reframeView:bottom withDeltas:CGRectMake(0, 9, 0, 0)];
    [waterMark addSubview:top];
    [waterMark addSubview:bottom];
    return waterMark;
}

+ (UIView*)waterMarkWithImage:(UIImage*)image title:(NSString*)title body:(NSString*)body options:(NSDictionary*)options {
    CGFloat width = 135;
    
    UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, width, 0)] autorelease];
    if (title) {
        UILabel* top = [Util viewWithText:title
                                     font:[UIFont stampedBoldFontWithSize:12]
                                    color:[UIColor stampedGrayColor]
                                     mode:UILineBreakModeTailTruncation
                               andMaxSize:CGSizeMake(width, CGFLOAT_MAX)];
        top.textAlignment = UITextAlignmentCenter;
        top.frame = [Util centeredAndBounded:top.frame.size inFrame:CGRectMake(0, 0, width, top.frame.size.height)];
        [Util appendView:top toParentView:view];
    }
    if (body) {
        UILabel* bottom = [Util viewWithText:body
                                        font:[UIFont stampedFontWithSize:12]
                                       color:[UIColor stampedGrayColor]
                                        mode:UILineBreakModeTailTruncation
                                  andMaxSize:CGSizeMake(135, CGFLOAT_MAX)];
        bottom.textAlignment = UITextAlignmentCenter;
        bottom.frame = [Util centeredAndBounded:bottom.frame.size inFrame:CGRectMake(0, 0, width, bottom.frame.size.height)];
        [Util appendView:bottom toParentView:view];
    }
    if (image) {
        UIImageView* waterMark = [[[UIImageView alloc] initWithImage:image] autorelease];
        waterMark.frame = [Util centeredAndBounded:waterMark.frame.size inFrame:CGRectMake(0, 0, width, waterMark.frame.size.height)];
        [Util appendView:waterMark toParentView:view];
    }
    return view;
}

@end
