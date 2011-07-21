//
//  Util.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface Util : NSObject

+ (void)splitHexString:(NSString*)hexString toRed:(CGFloat*)red green:(CGFloat*)green blue:(CGFloat*)blue;

@end
