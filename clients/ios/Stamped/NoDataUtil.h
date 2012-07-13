//
//  NoDataUtil.h
//  Stamped
//
//  Created by Landon Judkins on 7/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface NoDataUtil : NSObject

+ (UIView*)stampWatermarkWithTitle:(NSString*)title andSubtitle:(NSString*)subtitle;

+ (UIView*)waterMarkWithImage:(UIImage*)image title:(NSString*)title body:(NSString*)body options:(NSDictionary*)options;

@end
