//
//  CountriesViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import <UIKit/UIKit.h>

@protocol CountriesViewControllerDelegate;
@interface CountriesViewController : UITableViewController

@property(nonatomic,assign) id <CountriesViewControllerDelegate> delegate;
@property(nonatomic,copy) NSString *selectedCountry;

@end
@protocol CountriesViewControllerDelegate
- (void)contriesViewController:(CountriesViewController*)controller selectedCountry:(NSString*)country;
- (void)contriesViewControllerCancelled:(CountriesViewController*)controller;
@end