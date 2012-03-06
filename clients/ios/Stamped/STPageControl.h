//
//  STPageControl.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STPageControl : UIControl

@property(nonatomic) NSInteger currentPage;
@property(nonatomic) BOOL defersCurrentPageDisplay;
@property(nonatomic) BOOL hidesForSinglePage;
@property(nonatomic) NSInteger numberOfPages;

- (CGSize)  sizeForNumberOfPages:(NSInteger)pageCount;
- (void)    updateCurrentPageDisplay;

@end
