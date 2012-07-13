//
//  NoDataView.h
//
//  Created by Devin Doty on 2/9/11.
//  Copyright 2011. All rights reserved.
//


#import <UIKit/UIKit.h>

@class NoDataImageView;
@interface NoDataView : UIView 

@property(nonatomic,strong) UIImageView *imageView;
@property (nonatomic, readwrite, assign) BOOL custom;

- (void)setupWithTitle:(NSString*)title detailTitle:(NSString*)detailTitle; // setup helper

- (void)setupWithButtonTitle:(NSString*)title detailTitle:(NSString*)detailTitle target:(id)target andAction:(SEL)selector;

@end
